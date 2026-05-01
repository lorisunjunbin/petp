"""Unit tests for data_chain operations: populate_data, get_data, get_deep_data, loop data."""

import json
import logging


class TestPopulateData:

    def test_populate_new_key(self, make_processor, data_chain):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', data_chain)
        proc.populate_data("result", "hello")
        assert data_chain["result"] == "hello"

    def test_populate_overwrites_existing(self, make_processor, data_chain, caplog):
        data_chain["key"] = "old"
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', data_chain)
        with caplog.at_level(logging.WARNING):
            proc.populate_data("key", "new")
        assert data_chain["key"] == "new"
        assert "occupied and overwritten" in caplog.text

    def test_populate_none_value(self, make_processor, data_chain):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', data_chain)
        proc.populate_data("empty", None)
        assert data_chain["empty"] is None


class TestGetData:

    def test_get_existing_key(self, make_processor):
        chain = {"name": "petp"}
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', chain)
        assert proc.get_data("name") == "petp"

    def test_get_missing_key_returns_none(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        assert proc.get_data("nonexistent") is None

    def test_get_data_none_key_returns_none(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"a": 1})
        assert proc.get_data(None) is None

    def test_has_data(self, make_processor):
        chain = {"exists": "yes"}
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', chain)
        assert proc.has_data("exists") is True
        assert proc.has_data("nope") is False

    def test_del_data(self, make_processor):
        chain = {"to_delete": "value"}
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', chain)
        proc.del_data("to_delete")
        assert "to_delete" not in chain


class TestGetDeepData:

    def test_nested_access(self, make_processor):
        chain = {"a": {"b": {"c": "deep_value"}}}
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', chain)
        assert proc.get_deep_data(["a", "b", "c"]) == "deep_value"

    def test_nested_access_missing_intermediate(self, make_processor):
        chain = {"a": {"b": 1}}
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', chain)
        assert proc.get_deep_data(["a", "x", "y"]) is None


class TestDataChainJson:

    def test_serializable_data(self, make_processor):
        chain = {"key": "value", "num": 42, "list": [1, 2]}
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', chain)
        result = json.loads(proc.get_data_chain_json())
        assert result["key"] == "value"
        assert result["num"] == 42

    def test_non_serializable_fallback(self, make_processor):
        chain = {"obj": object()}
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', chain)
        result = proc.get_data_chain_json()
        assert "not-serializable" in result


class TestLoopData:

    def test_append_and_get_loop_data(self, make_processor, make_loop):
        loop = make_loop(code="my_loop", loop_times="3", loop_key="")
        chain = {"loop_idx": 0, "loop_item": "item_a"}
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', chain)
        proc.set_current_loop(loop)
        proc.set_in_loop(True)

        proc.append_data_for_loop("result", "iteration_0_data")

        assert chain["my_loop"][0]["result"] == "iteration_0_data"
        assert proc.get_data_by_loop("result") == "iteration_0_data"

    def test_append_multiple_iterations(self, make_processor, make_loop):
        loop = make_loop(code="iter_loop", loop_times="3", loop_key="")
        chain = {"loop_idx": 0, "loop_item": "a"}
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', chain)
        proc.set_current_loop(loop)
        proc.set_in_loop(True)

        proc.append_data_for_loop("val", "first")
        chain["loop_idx"] = 1
        proc.append_data_for_loop("val", "second")

        assert chain["iter_loop"][0]["val"] == "first"
        assert chain["iter_loop"][1]["val"] == "second"
