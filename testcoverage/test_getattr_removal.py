"""Security tests for P1-1: getattr/hasattr removal from _SAFE_BUILTINS.

The Phase 1 _SAFE_BUILTINS exposed getattr/hasattr — both enabled info disclosure
via dynamic attribute access (e.g. {getattr(p, "task").data_chain} exposes the
entire data_chain, including passwords and tokens). yaml expressions never
needed dynamic attribute names; removing both closes the vector with zero
real-world impact.
"""

import pytest


class TestGetattrHasattrRemoved:

    def test_getattr_unavailable_in_expression(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"secret": "s3cret"})
        # getattr is no longer a builtin → eval fails, expression2str returns
        # the original string unchanged (matches existing fallback behavior).
        result = proc.expression2str("{getattr(p, 'task')}")
        assert "Task" not in str(result)  # no Task object leaked
        # When eval fails for all 3 strategies, the literal string is returned.
        assert result == "{getattr(p, 'task')}"

    def test_hasattr_unavailable_in_expression(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        result = proc.expression2str("{hasattr(p, 'task')}")
        assert result == "{hasattr(p, 'task')}"

    def test_getattr_unavailable_in_fn_sandbox(self):
        # _fn function bodies share the same _SAFE_BUILTINS via Phase 2 P0-2.
        from utils.CodeExplainerUtil import CodeExplainerUtil
        with pytest.raises(NameError):
            CodeExplainerUtil.create_and_execute_func(
                "_t", "(p,)", "return getattr(p, '__class__')", object()
            )

    def test_hasattr_unavailable_in_fn_sandbox(self):
        from utils.CodeExplainerUtil import CodeExplainerUtil
        with pytest.raises(NameError):
            CodeExplainerUtil.create_and_execute_func(
                "_t2", "(p,)", "return hasattr(p, 'task')", object()
            )


class TestLegitimateExpressionsUnaffected:

    def test_p_get_data(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"k": "v"})
        assert proc.expression2str("{p.get_data('k')}") == "v"

    def test_self_get_tdir(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        assert "testcoverage" in proc.expression2str("{self.get_tdir()}")

    def test_safe_builtin_len(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"items": [1, 2, 3]})
        assert proc.expression2str("{len(items)}") == "3"

    def test_safe_builtin_str(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        assert proc.expression2str("{str(42)}") == "42"
