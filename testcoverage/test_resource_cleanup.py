"""Resource cleanup + bounded cache regression tests.

Covers:
- _expr_code_cache is a bounded LRUCache (no more unbounded growth from unique
  loop-generated f-strings).
- BackgroundRuntime / Executor cleanup quits selenium chrome drivers parked in
  data_chain when the execution exits via the exception path.
"""

import pytest
from cachetools import LRUCache


class TestExprCacheBounded:

    def test_expr_cache_is_lru(self):
        from core.processor import _expr_code_cache
        assert isinstance(_expr_code_cache, LRUCache)
        assert _expr_code_cache.maxsize == 2048

    def test_expr_cache_evicts_on_overflow(self):
        from core.processor import _expr_code_cache
        _expr_code_cache.clear()
        for i in range(_expr_code_cache.maxsize + 100):
            _expr_code_cache[f"expr_{i}"] = (0, compile("1", "<test>", "eval"))
        assert len(_expr_code_cache) <= _expr_code_cache.maxsize


class _FakeChromeDriver:
    """Mimics a selenium chrome webdriver — module/class name match the
    `selenium.webdriver.chrome.*` heuristic used by the cleanup path."""

    def __init__(self):
        self.quit_called = False

    def quit(self):
        self.quit_called = True


# `_is_chrome_driver_instance` checks the class's __module__, so spoof it.
_FakeChromeDriver.__module__ = "selenium.webdriver.chrome.webdriver"


class _BadChromeDriver(_FakeChromeDriver):
    def quit(self):
        raise RuntimeError("boom")


_BadChromeDriver.__module__ = "selenium.webdriver.chrome.webdriver"


class TestBackgroundRuntimeCleanup:

    def test_cleanup_invokes_quit_on_chrome_in_data_chain(self):
        from core.runtime.BackgroundRuntime import BackgroundRuntime
        rt = BackgroundRuntime(model=None)
        d = _FakeChromeDriver()
        data_chain = {"chrome": d, "other": "ignored", "num": 42}
        rt._cleanup_data_chain_drivers(data_chain)
        assert d.quit_called is True

    def test_cleanup_swallows_quit_errors(self):
        from core.runtime.BackgroundRuntime import BackgroundRuntime
        rt = BackgroundRuntime(model=None)
        # Should NOT raise even when driver.quit() blows up.
        rt._cleanup_data_chain_drivers({"chrome": _BadChromeDriver()})

    def test_cleanup_handles_non_dict_input(self):
        from core.runtime.BackgroundRuntime import BackgroundRuntime
        rt = BackgroundRuntime(model=None)
        # Should NOT raise — just no-op.
        rt._cleanup_data_chain_drivers(None)
        rt._cleanup_data_chain_drivers("not-a-dict")


class TestExecutorCleanup:

    def test_cleanup_invokes_quit_on_chrome_in_data_chain(self):
        from core.executor import Executor
        d = _FakeChromeDriver()
        Executor._cleanup_chrome_drivers({"chrome": d, "log": []})
        assert d.quit_called is True

    def test_cleanup_swallows_quit_errors(self):
        from core.executor import Executor
        Executor._cleanup_chrome_drivers({"chrome": _BadChromeDriver()})  # no raise


class TestToolsCacheNoTTL:

    def test_get_tools_cache_persists_without_ttl(self, monkeypatch):
        """Once built the manifest must not require a refresh — yaml is immutable
        post-startup in BG/Docker. Repeated calls return the same dict object."""
        from core.runtime.BackgroundRuntime import BackgroundRuntime
        rt = BackgroundRuntime(model=None)
        rt._tools_cache = {"FOO": '{"desc":"test"}'}
        first = rt.get_tools()
        second = rt.get_tools()
        assert first is second  # same object — no rebuild
        assert not hasattr(rt, '_TOOLS_CACHE_TTL')  # const removed
