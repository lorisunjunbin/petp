"""Unit tests for Processor.expression2str()."""

import os


class TestExpression2Str:

    def test_simple_variable_substitution(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"name": "world"})
        assert proc.expression2str("{name}") == "world"

    def test_multi_variable(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"a": "hello", "b": "world"})
        assert proc.expression2str("{a}/{b}") == "hello/world"

    def test_numeric_int_input(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        assert proc.expression2str(42) == "42"

    def test_numeric_float_input(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        assert proc.expression2str(3.14) == "3.14"

    def test_none_input_returns_none(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        assert proc.expression2str(None) is None

    def test_single_quote_in_expression_uses_strategy2(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"x": "test"})
        result = proc.expression2str("it's {x}")
        assert result == "it's test"

    def test_self_access(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        result = proc.expression2str("{self.get_tdir()}")
        assert "testcoverage" in result

    def test_os_module_access(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        result = proc.expression2str("{os.sep}")
        assert result == os.sep

    def test_json_module_access(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"data": [1, 2, 3]})
        result = proc.expression2str("{json.dumps(data)}")
        assert result == "[1, 2, 3]"

    def test_invalid_expression_returns_original(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        expr = "{undefined_var_xyz}"
        result = proc.expression2str(expr)
        assert result == expr

    def test_invalid_expression_none_if_not_matched(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        result = proc.expression2str("{undefined_var_xyz}", none_if_not_matched=True)
        assert result is None

    def test_python_arithmetic(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"x": 10})
        result = proc.expression2str("{x + 1}")
        assert result == "11"

    def test_cache_hit_returns_same_result(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"val": "cached"})
        result1 = proc.expression2str("{val}")
        result2 = proc.expression2str("{val}")
        assert result1 == result2 == "cached"

    def test_plain_string_no_braces(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        assert proc.expression2str("hello world") == "hello world"

    def test_empty_string(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        assert proc.expression2str("") == ""

    def test_get_json_param_raw_json_object_literal(self, make_processor):
        proc = make_processor("RUN_JAVASCRIPT", '{"params":"{\\"pyKey\\":1, \\"pyKey2\\":\\"dididadida\\"}"}', {})
        assert proc.get_json_param("params") == {"pyKey": 1, "pyKey2": "dididadida"}

    def test_get_json_param_with_expression_payload(self, make_processor):
        proc = make_processor("RUN_JAVASCRIPT", '{"params":"{json.dumps(payload)}"}', {"payload": {"pyKey": 7}})
        assert proc.get_json_param("params") == {"pyKey": 7}

    def test_extra_locals_resolves_var_absent_from_chain(self, make_processor):
        # extra_locals supplies a runtime var not in data_chain (e.g. {timeout}).
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        assert proc.expression2str("waited {timeout}s", extra_locals={"timeout": 10}) == "waited 10s"

    def test_extra_locals_shadows_chain_key(self, make_processor):
        # A like-named data_chain key must be shadowed by extra_locals, not win.
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"timeout": 999})
        assert proc.expression2str("{timeout}", extra_locals={"timeout": 10}) == "10"

    def test_extra_locals_does_not_mutate_chain(self, make_processor):
        chain = {"name": "x"}
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', chain)
        proc.expression2str("{timeout}", extra_locals={"timeout": 5})
        assert "timeout" not in chain  # extra_locals is layered, never written to the chain

    def test_extra_locals_combines_with_chain(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"who": "supplier A"})
        result = proc.expression2str("Can not find {who} in {timeout}s", extra_locals={"timeout": 30})
        assert result == "Can not find supplier A in 30s"

    def test_extra_locals_none_is_noop(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"name": "world"})
        assert proc.expression2str("{name}", extra_locals=None) == "world"

