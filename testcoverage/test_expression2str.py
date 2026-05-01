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
