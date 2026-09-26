"""OAuth2 resource-server JWT validation for the PETP HTTP/MCP layer.

When ``auth_mode: oauth2`` is configured, incoming bearer tokens are JWT
access tokens issued by an external IdP. This provider validates them
locally against the IdP's JWKS public keys — PETP acts as a pure Resource
Server and never handles user credentials.
"""
import logging
from typing import Optional

from utils.SecretUtil import resolve_secret

_BEARER_PREFIX = "Bearer "


class OAuth2JwtProvider:
    """Validates IdP-issued JWT bearer tokens (RS256 by default)."""

    def __init__(self, jwks_url: str, audience: Optional[str] = None,
                 issuer: Optional[str] = None,
                 algorithms: Optional[list] = None) -> None:
        self._audience = audience
        self._issuer = issuer
        self._algorithms = algorithms or ["RS256"]
        # Deferred import: pyjwt is only required when oauth2 auth is enabled.
        from jwt import PyJWKClient
        # cache_keys + lifespan let the client refresh keys without an extra
        # network round-trip per validation.
        self._jwks = PyJWKClient(jwks_url, cache_keys=True)

    def validate(self, auth_header: str) -> Optional[tuple]:
        """Return ``None`` when the token is valid, else ``(error, status)``.

        Any validation failure maps to 401 with a generic body — token detail
        is never leaked to the caller.
        """
        token = _extract_bearer(auth_header)
        if not token:
            return ({"error": "Unauthorized"}, 401)
        try:
            import jwt
            key = self._jwks.get_signing_key_from_jwt(token).key
            jwt.decode(token, key, algorithms=self._algorithms,
                       audience=self._audience, issuer=self._issuer)
        except Exception as e:  # noqa: BLE001 — any failure = reject, no detail leak
            logging.warning("OAuth2 JWT validation failed: %s", e)
            return ({"error": "Unauthorized"}, 401)
        return None


def _extract_bearer(auth_header: str) -> str:
    """Strip the optional ``Bearer `` prefix, mirroring static-token auth."""
    if auth_header.startswith(_BEARER_PREFIX):
        return auth_header[len(_BEARER_PREFIX):]
    return auth_header


def build_auth_provider(model) -> Optional[OAuth2JwtProvider]:
    """Build the OAuth2 provider from config, or ``None`` for static-token mode.

    Fail-closed: ``auth_mode: oauth2`` with a missing ``oauth2_jwks_url``
    returns ``None``, so ``_require_token`` falls through to static-token
    auth (which itself returns 501 when no static token is set).
    """
    mode = getattr(model, 'auth_mode', 'static')
    if mode != 'oauth2':
        return None
    jwks_url = resolve_secret(getattr(model, 'oauth2_jwks_url', '') or '')
    if not jwks_url:
        logging.error("auth_mode=oauth2 but oauth2_jwks_url is not configured")
        return None
    audience = getattr(model, 'oauth2_audience', '') or None
    issuer = getattr(model, 'oauth2_issuer', '') or None
    return OAuth2JwtProvider(jwks_url=jwks_url, audience=audience, issuer=issuer)
