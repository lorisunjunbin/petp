"""Tests for HTTP request size guards — Phase 2 P1-3.

Verifies that oversize JSON bodies (>MAX_BODY_BYTES) and oversize batch
arrays (>MAX_BATCH_ITEMS) are rejected before reaching the routing layer.
Both limits are env-tunable via PETP_MAX_BODY_BYTES and PETP_MAX_BATCH_ITEMS.
"""
import io
import json
from unittest.mock import MagicMock

import pytest


def _make_handler(body_bytes: bytes, content_type: str = "application/json", method: str = "POST"):
    """Build a minimally functional HttpRequestHandler instance for parse_request_params."""
    from httpservice.handlers.HttpRequestHandler import HttpRequestHandler

    h = HttpRequestHandler.__new__(HttpRequestHandler)
    h.command = method
    h.path = "/petp/exec"
    h.headers = {
        "Content-Length": str(len(body_bytes)),
        "Content-Type": content_type,
    }
    h.rfile = io.BytesIO(body_bytes)
    h.send_error = MagicMock()
    return h


class TestBodySizeLimit:

    def test_body_under_limit_accepted(self):
        body = json.dumps({"action": "execution", "params": {}}).encode("utf-8")
        h = _make_handler(body)
        result = h.parse_request_params()
        assert result is not None
        params, _ = result
        assert params["action"] == "execution"
        h.send_error.assert_not_called()

    def test_body_over_limit_rejected(self, monkeypatch):
        from httpservice.handlers import HttpRequestHandler as mod
        monkeypatch.setattr(mod, "MAX_BODY_BYTES", 100)

        body = b"x" * 200  # exceeds 100 bytes
        h = _make_handler(body)
        result = h.parse_request_params()
        assert result is None
        h.send_error.assert_called_once()
        args, kwargs = h.send_error.call_args
        assert args[0] == 413  # Payload Too Large

    def test_body_at_limit_accepted(self, monkeypatch):
        from httpservice.handlers import HttpRequestHandler as mod
        monkeypatch.setattr(mod, "MAX_BODY_BYTES", 200)

        body = json.dumps({"k": "v" * 80}).encode("utf-8")
        assert len(body) <= 200
        h = _make_handler(body)
        result = h.parse_request_params()
        assert result is not None


class TestBatchSizeLimit:

    def test_batch_under_limit_accepted(self):
        batch = [{"jsonrpc": "2.0", "id": str(i), "method": "tools/list"} for i in range(5)]
        body = json.dumps(batch).encode("utf-8")
        h = _make_handler(body)
        result = h.parse_request_params()
        assert result is not None
        params, _ = result
        assert "_batch" in params
        assert len(params["_batch"]) == 5

    def test_batch_over_limit_rejected(self, monkeypatch):
        from httpservice.handlers import HttpRequestHandler as mod
        monkeypatch.setattr(mod, "MAX_BATCH_ITEMS", 10)

        batch = [{"jsonrpc": "2.0", "id": str(i), "method": "tools/list"} for i in range(20)]
        body = json.dumps(batch).encode("utf-8")
        h = _make_handler(body)
        result = h.parse_request_params()
        assert result is None
        h.send_error.assert_called_once()
        args, _ = h.send_error.call_args
        assert args[0] == 400

    def test_batch_at_limit_accepted(self, monkeypatch):
        from httpservice.handlers import HttpRequestHandler as mod
        monkeypatch.setattr(mod, "MAX_BATCH_ITEMS", 8)

        batch = [{"jsonrpc": "2.0", "id": str(i), "method": "tools/list"} for i in range(8)]
        body = json.dumps(batch).encode("utf-8")
        h = _make_handler(body)
        result = h.parse_request_params()
        assert result is not None


class TestEnvVarParsing:

    def test_int_env_default_when_unset(self, monkeypatch):
        monkeypatch.delenv("PETP_TEST_VAR", raising=False)
        from httpservice.handlers.HttpRequestHandler import _int_env
        assert _int_env("PETP_TEST_VAR", 42) == 42

    def test_int_env_default_when_invalid(self, monkeypatch):
        monkeypatch.setenv("PETP_TEST_VAR", "not_a_number")
        from httpservice.handlers.HttpRequestHandler import _int_env
        assert _int_env("PETP_TEST_VAR", 42) == 42

    def test_int_env_default_when_zero_or_negative(self, monkeypatch):
        from httpservice.handlers.HttpRequestHandler import _int_env
        monkeypatch.setenv("PETP_TEST_VAR", "0")
        assert _int_env("PETP_TEST_VAR", 42) == 42
        monkeypatch.setenv("PETP_TEST_VAR", "-5")
        assert _int_env("PETP_TEST_VAR", 42) == 42

    def test_int_env_overrides(self, monkeypatch):
        monkeypatch.setenv("PETP_TEST_VAR", "999")
        from httpservice.handlers.HttpRequestHandler import _int_env
        assert _int_env("PETP_TEST_VAR", 42) == 999
