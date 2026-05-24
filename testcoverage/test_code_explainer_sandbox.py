"""Security tests for CodeExplainerUtil dynamic function sandbox.

P0-2: exec(func, globals()) gave _fn parameters access to full __builtins__,
including __import__, open, eval, exec, etc — a full sandbox bypass for any
processor with a *_fn / *_func_body / lambda_* parameter. Fix: exec into a
restricted namespace whose __builtins__ is Processor._SAFE_BUILTINS.

PoC strategy: try to break out of the sandbox via several known vectors.
Each must raise (typically NameError or AttributeError).
"""

import os
import pytest

from utils.CodeExplainerUtil import CodeExplainerUtil


def _exec_body(body, args=None, *extra):
    return CodeExplainerUtil.create_and_execute_func(
        "_test_fn", "(*_args, **_kwargs)", body, args, *extra
    )


class TestSandboxBlocksDangerousBuiltins:

    def test_blocks_import(self):
        with pytest.raises(NameError):
            _exec_body("return __import__('os').system('echo BREAK')", 1)

    def test_blocks_open(self):
        with pytest.raises(NameError):
            _exec_body("return open('/etc/passwd').read()", 1)

    def test_blocks_eval(self):
        with pytest.raises(NameError):
            _exec_body("return eval('1+1')", 1)

    def test_blocks_exec(self):
        with pytest.raises(NameError):
            _exec_body("return exec('x=1')", 1)

    def test_blocks_compile(self):
        with pytest.raises(NameError):
            _exec_body("return compile('1','<x>','eval')", 1)

    def test_blocks_globals(self):
        with pytest.raises(NameError):
            _exec_body("return globals()", 1)

    def test_blocks_vars(self):
        with pytest.raises(NameError):
            _exec_body("return vars()", 1)

    def test_blocks_os_module_in_globals(self):
        # The old code did `exec(func, globals())` — the module-level `globals()`
        # was the CodeExplainerUtil module's namespace, which imported `logging`.
        # Now `logging` must not be reachable from inside the sandbox.
        with pytest.raises(NameError):
            _exec_body("return logging", 1)


class TestSandboxAllowsLegitimateUse:

    def test_simple_arithmetic(self):
        result = _exec_body("return _args[0] + 1", 5)
        assert result == 6

    def test_safe_builtin_len(self):
        result = _exec_body("return len(_args[0])", "hello")
        assert result == 5

    def test_safe_builtin_str(self):
        result = _exec_body("return str(_args[0])", 42)
        assert result == "42"

    def test_list_comprehension(self):
        result = _exec_body("return [x*2 for x in _args[0]]", [1, 2, 3])
        assert result == [2, 4, 6]

    def test_whitelisted_re_module(self):
        result = _exec_body("return re.findall(r'\\d+', _args[0])", "abc123def456")
        assert result == ["123", "456"]

    def test_whitelisted_json_module(self):
        result = _exec_body('return json.dumps({"a": _args[0]})', 1)
        assert result == '{"a": 1}'

    def test_whitelisted_datetime_module(self):
        result = _exec_body(
            "return datetime.date(2026, 1, 1).isoformat()", 1
        )
        assert result == "2026-01-01"

    def test_p_method_access(self):
        # Real-world _fn signatures use `p` for the Processor; the sandbox does
        # NOT block calling methods on `p` — that's the legitimate API.
        class FakeP:
            def get_data(self, k):
                return f"value_of_{k}"

        result = CodeExplainerUtil.create_and_execute_func(
            "_test_with_p", "(p, key)", "return p.get_data(key)", FakeP(), "k1"
        )
        assert result == "value_of_k1"


class TestSandboxCacheIsolation:

    def test_cached_function_uses_sandbox(self):
        # First call caches the compiled function; second call must still raise.
        body = "return __import__('os')"
        try:
            _exec_body(body, 1)
        except NameError:
            pass
        # Second call (cache hit path)
        with pytest.raises(NameError):
            _exec_body(body, 1)
