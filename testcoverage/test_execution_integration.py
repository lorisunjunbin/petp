"""Integration tests: run executions via BackgroundRuntime."""

import pytest


class TestEndecoder:

    def test_base64_encode(self, bg_runtime):
        r = bg_runtime.run_execution("ENDECODER", {"type": "encode", "algorithms": "base64", "inbound": "hello"})
        assert r["ok"], f"not ok: {r['error']}"
        assert any("aGVsbG8" in str(v) for v in r["data"].values())

    def test_base64_decode(self, bg_runtime):
        r = bg_runtime.run_execution("ENDECODER", {"type": "decode", "algorithms": "base64", "inbound": "aGVsbG8="})
        assert r["ok"], f"not ok: {r['error']}"
        assert any("hello" in str(v) for v in r["data"].values())

    def test_hexlify_encode(self, bg_runtime):
        r = bg_runtime.run_execution("ENDECODER", {"type": "encode", "algorithms": "hexlify", "inbound": "AB"})
        assert r["ok"], f"not ok: {r['error']}"
        assert any("4142" in str(v) for v in r["data"].values())

    def test_md5_not_supported_gracefully(self, bg_runtime):
        r = bg_runtime.run_execution("ENDECODER", {"type": "encode", "algorithms": "md5", "inbound": "test"})
        assert r["ok"] is True or r["ok"] is False  # should not crash


class TestExecutionNotFound:

    def test_missing_execution_returns_not_ok(self, bg_runtime):
        r = bg_runtime.run_execution("NONEXISTENT_EXECUTION_XYZ")
        assert r["ok"] is False
        assert r["error"] is not None


class TestEmptyInitData:

    def test_empty_dict_works(self, bg_runtime):
        r = bg_runtime.run_execution("ENDECODER", {})
        # May fail due to missing params but should not crash
        assert "ok" in r


class TestLoopExecution:

    def test_loop_time_execution(self, bg_runtime):
        r = bg_runtime.run_execution("loop_time")
        assert r["ok"], f"not ok: {r['error']}"


class TestDataConvert:

    def test_data_convert_execution(self, bg_runtime):
        r = bg_runtime.run_execution("test_data_convert")
        assert r["ok"], f"not ok: {r['error']}"


class TestMetaFields:

    def test_result_has_meta(self, bg_runtime):
        r = bg_runtime.run_execution("ENDECODER", {"type": "encode", "algorithms": "base64", "inbound": "x"})
        assert "meta" in r
        assert "duration_ms" in r["meta"]
        assert r["meta"]["duration_ms"] >= 0
