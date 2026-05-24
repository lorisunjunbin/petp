"""Tests for log redaction utility — Phase 2 P1-4.

Verifies that sensitive keys (api_key, password, token, etc.) in JSON
inputs and arbitrary strings are masked before reaching log files.
PETP_LOG_REDACT=off must bypass entirely.
"""
import json

import pytest

from utils.LogRedactor import redact_sensitive


class TestJsonDictRedaction:

    def test_top_level_api_key_masked(self):
        out = redact_sensitive('{"api_key": "sk-secret-123", "model": "gpt-4"}')
        parsed = json.loads(out)
        assert parsed["api_key"] == "***REDACTED***"
        assert parsed["model"] == "gpt-4"

    def test_nested_password_masked(self):
        payload = '{"db": {"host": "x", "password": "p@ss"}}'
        out = redact_sensitive(payload)
        parsed = json.loads(out)
        assert parsed["db"]["host"] == "x"
        assert parsed["db"]["password"] == "***REDACTED***"

    def test_authorization_header_masked(self):
        payload = '{"headers": {"Authorization": "Bearer abc123", "User-Agent": "petp"}}'
        out = redact_sensitive(payload)
        parsed = json.loads(out)
        assert parsed["headers"]["Authorization"] == "***REDACTED***"
        assert parsed["headers"]["User-Agent"] == "petp"

    def test_case_insensitive_match(self):
        payload = '{"API_KEY": "x", "Token": "y", "PASSWORD": "z"}'
        out = redact_sensitive(payload)
        parsed = json.loads(out)
        assert parsed["API_KEY"] == "***REDACTED***"
        assert parsed["Token"] == "***REDACTED***"
        assert parsed["PASSWORD"] == "***REDACTED***"

    def test_substring_match(self):
        payload = '{"my_api_key_env": "OPENAI_KEY", "smtp_password": "p"}'
        out = redact_sensitive(payload)
        parsed = json.loads(out)
        assert parsed["my_api_key_env"] == "***REDACTED***"
        assert parsed["smtp_password"] == "***REDACTED***"

    def test_non_sensitive_keys_preserved(self):
        payload = '{"url": "https://api.example.com", "method": "POST", "data": {"x": 1}}'
        out = redact_sensitive(payload)
        parsed = json.loads(out)
        assert parsed["url"] == "https://api.example.com"
        assert parsed["data"]["x"] == 1


class TestJsonListRedaction:

    def test_array_of_dicts_redacted(self):
        payload = '[{"name": "a", "secret": "s1"}, {"name": "b", "token": "t1"}]'
        out = redact_sensitive(payload)
        parsed = json.loads(out)
        assert parsed[0]["secret"] == "***REDACTED***"
        assert parsed[1]["token"] == "***REDACTED***"
        assert parsed[0]["name"] == "a"

    def test_dict_object_input(self):
        out = redact_sensitive({"api_key": "x", "name": "y"})
        parsed = json.loads(out)
        assert parsed["api_key"] == "***REDACTED***"
        assert parsed["name"] == "y"


class TestNonJsonFallback:

    def test_kv_string_fallback(self):
        # Looks like JSON but malformed — fallback to regex
        payload = '{"api_key": "x", invalid'
        out = redact_sensitive(payload)
        assert '"api_key": "***REDACTED***"' in out

    def test_plain_text_with_kv_pattern(self):
        # Not JSON at all — regex still kicks in
        payload = 'request: "password": "leaked123" and stuff'
        out = redact_sensitive(payload)
        assert '"password": "***REDACTED***"' in out
        assert 'leaked123' not in out

    def test_plain_text_no_sensitive(self):
        payload = "just a plain log message about the weather"
        out = redact_sensitive(payload)
        assert out == payload


class TestDisableViaEnv:

    def test_env_off_bypasses(self, monkeypatch):
        monkeypatch.setenv("PETP_LOG_REDACT", "off")
        payload = '{"api_key": "secret123"}'
        out = redact_sensitive(payload)
        assert out == payload
        assert "secret123" in out

    def test_env_on_default(self, monkeypatch):
        monkeypatch.delenv("PETP_LOG_REDACT", raising=False)
        payload = '{"api_key": "secret123"}'
        out = redact_sensitive(payload)
        assert "***REDACTED***" in out

    def test_env_other_values_redact(self, monkeypatch):
        monkeypatch.setenv("PETP_LOG_REDACT", "on")
        payload = '{"token": "x"}'
        assert "***REDACTED***" in redact_sensitive(payload)


class TestEdgeCases:

    def test_empty_string(self):
        assert redact_sensitive("") == ""

    def test_none_value(self):
        assert redact_sensitive(None) == "None"

    def test_int_value(self):
        assert redact_sensitive(42) == "42"

    def test_malformed_json_falls_back(self):
        payload = '{not valid json "secret": "x"}'
        out = redact_sensitive(payload)
        assert '"secret": "***REDACTED***"' in out

    def test_never_raises(self):
        # Arbitrary objects fall back to str() — no redaction, but no crash.
        class Weird:
            def __str__(self):
                return 'whatever'
        out = redact_sensitive(Weird())
        assert isinstance(out, str)
        assert out == 'whatever'

    def test_deeply_nested(self):
        payload = json.dumps({
            "level1": {
                "level2": {
                    "level3": {
                        "api_key": "deep-secret",
                        "ok": "visible",
                    }
                }
            }
        })
        out = redact_sensitive(payload)
        parsed = json.loads(out)
        assert parsed["level1"]["level2"]["level3"]["api_key"] == "***REDACTED***"
        assert parsed["level1"]["level2"]["level3"]["ok"] == "visible"
