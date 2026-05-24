"""Log redaction utility — Phase 2 P1-4.

Many processors include credentials in their `input` JSON: API keys,
Authorization headers, DB passwords, SMTP passwords, OAuth tokens. Three log
sites print the entire `task.input` blob at INFO level
(`Execution.run`, `BackgroundRuntime.run_execution`, `Processor.do_process`).
On long-running BG/Docker deployments, log files / centralized log shipping
can leak these credentials.

`redact_sensitive(s)` walks JSON-string or arbitrary-string input and
replaces values whose key matches a sensitive pattern with `***REDACTED***`.
Best-effort: if the input is not JSON, regex falls back to
`"sensitive_key": "<redacted>"` rewriting. Never raises — log code must not
crash the pipeline.

Sensitive key patterns (case-insensitive, substring match):
  api_key, apikey, access_key, secret, password, passwd, token, authorization,
  bearer, auth, private_key, salt, pwd

Disable with PETP_LOG_REDACT=off (default: on). Useful only for ad-hoc
debugging where you accept the leakage risk.
"""
import json
import logging
import os
import re
from typing import Any

_logger = logging.getLogger(__name__)

_SENSITIVE_PATTERNS = (
    'api_key', 'apikey', 'access_key', 'secret', 'password', 'passwd',
    'token', 'authorization', 'bearer', 'auth', 'private_key', 'salt', 'pwd',
)

_REDACTED = '***REDACTED***'

# Pattern for non-JSON fallback: "key": "value" or "key":"value" with whitespace tolerance.
_KV_FALLBACK = re.compile(
    r'("(?:' + '|'.join(_SENSITIVE_PATTERNS) + r')[^"]*"\s*:\s*)"[^"]*"',
    re.IGNORECASE,
)


def _is_redact_enabled() -> bool:
    return os.environ.get('PETP_LOG_REDACT', 'on').strip().lower() != 'off'


def _is_sensitive_key(key: str) -> bool:
    k = key.lower()
    return any(p in k for p in _SENSITIVE_PATTERNS)


def _redact_obj(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(k, str) and _is_sensitive_key(k):
                out[k] = _REDACTED
            else:
                out[k] = _redact_obj(v)
        return out
    if isinstance(obj, list):
        return [_redact_obj(x) for x in obj]
    return obj


def redact_sensitive(value: Any) -> str:
    """Return a string safe to log: sensitive values masked.

    Accepts JSON strings, dicts, lists, or arbitrary objects. Never raises.
    When PETP_LOG_REDACT=off, returns str(value) unchanged.
    """
    if not _is_redact_enabled():
        return str(value)

    try:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith(('{', '[')):
                try:
                    parsed = json.loads(stripped)
                    return json.dumps(_redact_obj(parsed), ensure_ascii=False)
                except (json.JSONDecodeError, ValueError):
                    return _KV_FALLBACK.sub(lambda m: m.group(1) + f'"{_REDACTED}"', value)
            return _KV_FALLBACK.sub(lambda m: m.group(1) + f'"{_REDACTED}"', value)

        if isinstance(value, (dict, list)):
            return json.dumps(_redact_obj(value), ensure_ascii=False, default=str)

        return str(value)
    except Exception as exc:
        _logger.debug('redact_sensitive: fell back to str() (%s)', exc)
        return str(value)
