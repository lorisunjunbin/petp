"""Environment-variable secret resolution for PETP config values.

Config fields may reference an environment variable with ``${VAR}`` syntax
(e.g. ``http_request_token: ${PETP_HTTP_TOKEN}``). The real secret is then
injected at runtime instead of being committed to YAML.
"""
import os
import re

_ENV_PATTERN = re.compile(r'\$\{(.+)\}')


def resolve_secret(raw: str) -> str:
    """Resolve a ``${ENV_VAR}`` reference to its environment value.

    Returns the environment variable's value when ``raw`` is exactly a
    ``${VAR}`` reference, otherwise returns ``raw`` unchanged. An unset
    variable resolves to ``''`` so downstream fail-closed logic (e.g.
    ``_require_token``) rejects requests rather than accepting an empty
    secret.
    """
    if not raw:
        return ''
    match = _ENV_PATTERN.fullmatch(raw.strip())
    if match:
        return os.environ.get(match.group(1), '')
    return raw
