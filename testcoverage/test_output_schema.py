"""Unit + integration tests for the mcp_desc.outputSchema field mapping that lets a
headless run() (BackgroundRuntime.run_execution) return the SAME shaped output as the
MCP layer, instead of the whole data_chain.

Covers:
- BackgroundRuntime._map_output_schema: the pure mapping rules (mapKey direct,
  f-string expression, string coercion, missing-key skip, input-param exclusion).
- Execution.get_output_schema: parsing outputSchema out of mcp_desc (present /
  absent / malformed / cached).
- run_execution precedence: outputSchema (field mapping) > HTTP_RESPONSE_KEY >
  full data_chain — verified end-to-end with a mocked Execution so no browser or
  real execution file is needed.
"""

import json
from unittest import mock

import pytest

from core.runtime.BackgroundRuntime import BackgroundRuntime
from core.execution import Execution
from core.constants import HTTP_RESPONSE_KEY


class TestMapOutputSchema:

    def test_mapkey_direct_lookup(self):
        schema = {"properties": {"result": {"mapKey": "final_answer"}}}
        out = BackgroundRuntime._map_output_schema({"final_answer": 42}, schema)
        assert out == {"result": 42}

    def test_property_name_used_when_no_mapkey(self):
        schema = {"properties": {"final_answer": {}}}
        out = BackgroundRuntime._map_output_schema({"final_answer": 7}, schema)
        assert out == {"final_answer": 7}

    def test_fstring_expression_mapkey(self):
        schema = {"properties": {"combo": {"mapKey": "{a}-{b}"}}}
        out = BackgroundRuntime._map_output_schema({"a": "x", "b": "y"}, schema)
        assert out == {"combo": "x-y"}

    def test_string_type_coerces_non_string(self):
        schema = {"properties": {"r": {"mapKey": "n", "type": "string"}}}
        out = BackgroundRuntime._map_output_schema({"n": 99}, schema)
        assert out == {"r": "99"}  # int -> JSON string

    def test_string_type_serializes_dict(self):
        schema = {"properties": {"obj": {"mapKey": "payload", "type": "string"}}}
        out = BackgroundRuntime._map_output_schema({"payload": {"k": 1}}, schema)
        assert out == {"obj": '{"k": 1}'}

    def test_missing_key_is_skipped(self):
        schema = {"properties": {"present": {"mapKey": "a"}, "gone": {"mapKey": "nope"}}}
        out = BackgroundRuntime._map_output_schema({"a": 1}, schema)
        assert out == {"present": 1}
        assert "gone" not in out

    def test_input_param_excluded_when_not_mapped(self):
        # A data_chain key that the schema does not name must NOT appear in output.
        schema = {"properties": {"result": {"mapKey": "final_answer"}}}
        out = BackgroundRuntime._map_output_schema(
            {"final_answer": 1, "supplier_name": "ACME"}, schema)
        assert out == {"result": 1}
        assert "supplier_name" not in out

    def test_bad_fstring_expression_skips_property(self):
        # An expression referencing an absent var raises inside eval -> skip, not crash.
        schema = {"properties": {"combo": {"mapKey": "{missing_var}"}}}
        out = BackgroundRuntime._map_output_schema({"a": 1}, schema)
        assert out == {}

    def test_non_dict_data_returns_empty(self):
        assert BackgroundRuntime._map_output_schema(None, {"properties": {}}) == {}
        assert BackgroundRuntime._map_output_schema("x", {"properties": {}}) == {}

    def test_empty_properties_returns_empty(self):
        assert BackgroundRuntime._map_output_schema({"a": 1}, {"properties": {}}) == {}


class TestGetOutputSchema:

    def test_returns_schema_from_mcp_desc(self):
        ex = Execution("X", [], mcp_desc=json.dumps(
            {"outputSchema": {"properties": {"r": {"mapKey": "final_answer", "type": "string"}}}}),
            astool=True)
        s = ex.get_output_schema()
        assert s["properties"]["r"]["mapKey"] == "final_answer"

    def test_empty_when_no_mcp_desc(self):
        assert Execution("Y", [], mcp_desc="", astool=False).get_output_schema() == {}

    def test_empty_when_no_output_schema_key(self):
        ex = Execution("Z", [], mcp_desc=json.dumps({"desc": "hi", "params": ["a"]}), astool=True)
        assert ex.get_output_schema() == {}

    def test_empty_when_output_schema_has_no_properties(self):
        ex = Execution("W", [], mcp_desc=json.dumps({"outputSchema": {}}), astool=True)
        assert ex.get_output_schema() == {}

    def test_empty_on_malformed_mcp_desc(self):
        ex = Execution("M", [], mcp_desc="{not valid json", astool=True)
        assert ex.get_output_schema() == {}

    def test_result_is_cached(self):
        ex = Execution("C", [], mcp_desc=json.dumps(
            {"outputSchema": {"properties": {"r": {"mapKey": "a"}}}}), astool=True)
        first = ex.get_output_schema()
        second = ex.get_output_schema()
        assert first is second  # cached object identity


class TestRunExecutionPrecedence:
    """End-to-end: an Execution with an empty task list falls straight through to
    the success return, so data == init_data after mapping. We mock get_execution /
    expand_mcp_defaults to avoid real execution files and MCP default expansion."""

    def _runtime(self):
        return BackgroundRuntime(model=None)

    def _run_with(self, ex, init_data):
        with mock.patch.object(Execution, "get_execution", staticmethod(lambda name: ex)), \
             mock.patch.object(Execution, "expand_mcp_defaults", lambda self, dc: {}):
            return self._runtime().run_execution("ANY", init_data)

    def test_output_schema_returns_only_mapped_fields(self):
        ex = Execution("E1", [], mcp_desc=json.dumps(
            {"outputSchema": {"properties": {"result": {"mapKey": "final_answer", "type": "string"}}}}),
            astool=True)
        r = self._run_with(ex, {"supplier_name": "ACME", "final_answer": 99})
        assert r["ok"] is True
        assert r["data"] == {"result": "99"}
        assert "supplier_name" not in r["data"]  # input param excluded

    def test_no_schema_returns_full_data_chain(self):
        ex = Execution("E2", [], mcp_desc="", astool=False)
        r = self._run_with(ex, {"supplier_name": "ACME", "final_answer": 99})
        assert r["ok"] is True
        # unchanged behavior: whole (serializable, non-internal) data_chain returned
        assert r["data"].get("supplier_name") == "ACME"
        assert r["data"].get("final_answer") == 99

    def test_failure_path_not_mapped(self):
        # Execution not found -> ok=False, data={}, schema mapping never applied.
        with mock.patch.object(Execution, "get_execution", staticmethod(lambda name: None)):
            r = self._runtime().run_execution("MISSING", {"x": 1})
        assert r["ok"] is False
        assert r["data"] == {}
        assert r["error"]

    def test_apply_output_schema_false_returns_full_chain(self):
        # The MCP layer maps outputSchema itself, so it calls run_execution with
        # apply_output_schema=False to avoid mapping twice (which would drop fields
        # whose mapKey differs from the property name). With the flag off, the raw
        # data_chain — including the original mapKey source keys — must survive.
        ex = Execution("E3", [], mcp_desc=json.dumps(
            {"outputSchema": {"properties": {"result": {"mapKey": "final_answer", "type": "string"}}}}),
            astool=True)
        with mock.patch.object(Execution, "get_execution", staticmethod(lambda name: ex)), \
             mock.patch.object(Execution, "expand_mcp_defaults", lambda self, dc: {}):
            r = self._runtime().run_execution("ANY", {"final_answer": 99, "supplier_name": "ACME"},
                                              apply_output_schema=False)
        assert r["ok"] is True
        # NOT mapped: original data_chain keys preserved for the MCP layer to map.
        assert r["data"].get("final_answer") == 99
        assert "result" not in r["data"]


class TestLogDeclaredOutput:
    """Execution._log_declared_output (GUI path): log the declared output so a GUI
    run surfaces the same result an MCP/HTTP caller would get. outputSchema >
    HTTP_RESPONSE_KEY; neither declared -> no log."""

    def test_logs_output_schema_mapping(self, caplog):
        ex = Execution("E1", [], mcp_desc=json.dumps(
            {"outputSchema": {"properties": {"result": {"mapKey": "final_answer", "type": "string"}}}}),
            astool=True)
        with caplog.at_level("INFO"):
            ex._log_declared_output({"final_answer": 99, "supplier_name": "ACME"})
        assert "outputSchema" in caplog.text
        assert '"result": "99"' in caplog.text
        assert "supplier_name" not in caplog.text  # only mapped fields logged

    def test_logs_http_response_key_value(self, caplog):
        ex = Execution("E2", [], mcp_desc="", astool=False)
        with caplog.at_level("INFO"):
            ex._log_declared_output({HTTP_RESPONSE_KEY: "my_out", "my_out": {"k": 1}, "other": 2})
        assert "HTTP_RESPONSE_KEY=my_out" in caplog.text
        assert '"k": 1' in caplog.text

    def test_no_declared_output_logs_nothing(self, caplog):
        ex = Execution("E3", [], mcp_desc="", astool=False)
        with caplog.at_level("INFO"):
            ex._log_declared_output({"a": 1, "b": 2})
        assert "output" not in caplog.text  # plain executions stay silent

    def test_run_calls_log_declared_output(self):
        # Execution.run() invokes _log_declared_output once on the normal finish path.
        ex = Execution("E4", [], mcp_desc="")
        from threading import Condition
        with mock.patch.object(Execution, "_log_declared_output") as m:
            ex.run({"x": 1}, Condition(), None)
        m.assert_called_once()
