"""Tests for OAuth2 JWT validation (resource server).

Covers OAuth2JwtProvider.validate() against a real in-process JWKS endpoint:
valid, expired, wrong audience/issuer, tampered signature, garbage/missing
header, plus the build_auth_provider fail-closed config wiring.

Run: pytest testcoverage/test_oauth2_jwt.py -v
"""

import base64
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from httpservice.auth.OAuth2JwtProvider import (
    OAuth2JwtProvider,
    _extract_bearer,
    build_auth_provider,
)


# ---------------------------------------------------------------------------
# Helpers — in-process JWKS server + RSA keypair
# ---------------------------------------------------------------------------

def _b64url_int(i: int) -> str:
    """Base64url-encode a positive int (JWK n/e fields, no padding)."""
    b = i.to_bytes((i.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def _make_keypair():
    from cryptography.hazmat.primitives.asymmetric import rsa
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _jwk_from_key(key) -> dict:
    nums = key.public_key().public_numbers()
    return {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": "test-key",
        "n": _b64url_int(nums.n),
        "e": _b64url_int(nums.e),
    }


def _private_pem(key) -> bytes:
    from cryptography.hazmat.primitives import serialization
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )


_JWKS_BYTES = b""


class _JwksHandler(BaseHTTPRequestHandler):
    """Serves a static JWKS document at any path."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(_JWKS_BYTES)))
        self.end_headers()
        self.wfile.write(_JWKS_BYTES)

    def log_message(self, *args):  # silence per-request logging
        pass


@pytest.fixture(scope="module")
def jwks_server():
    """Start an in-process HTTP server exposing one RSA JWKS key."""
    global _JWKS_BYTES
    key = _make_keypair()
    _JWKS_BYTES = json.dumps({"keys": [_jwk_from_key(key)]}).encode("utf-8")
    server = ThreadingHTTPServer(("127.0.0.1", 0), _JwksHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield {
        "url": f"http://127.0.0.1:{server.server_address[1]}/jwks",
        "private_key": key,
    }
    server.shutdown()
    server.server_close()


def _sign(jwks_server, payload: dict) -> str:
    """Sign a JWT with the fixture's RSA key, matching the JWKS 'kid'."""
    import jwt
    return jwt.encode(
        payload,
        _private_pem(jwks_server["private_key"]),
        algorithm="RS256",
        headers={"kid": "test-key"},
    )


# ---------------------------------------------------------------------------
# validate() — positive & negative
# ---------------------------------------------------------------------------

class TestJwtValidation:

    def _provider(self, jwks_server) -> OAuth2JwtProvider:
        return OAuth2JwtProvider(
            jwks_url=jwks_server["url"],
            audience="petp",
            issuer="https://idp.example.com",
        )

    def _claims(self, **overrides) -> dict:
        claims = {
            "sub": "user-123",
            "aud": "petp",
            "iss": "https://idp.example.com",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        }
        claims.update(overrides)
        return claims

    def test_valid_token_returns_none(self, jwks_server):
        provider = self._provider(jwks_server)
        token = _sign(jwks_server, self._claims())
        assert provider.validate(f"Bearer {token}") is None

    def test_bare_token_without_bearer_prefix(self, jwks_server):
        provider = self._provider(jwks_server)
        token = _sign(jwks_server, self._claims())
        assert provider.validate(token) is None

    def test_missing_authorization_returns_401(self, jwks_server):
        provider = self._provider(jwks_server)
        body, status = provider.validate("")
        assert status == 401
        assert body == {"error": "Unauthorized"}

    def test_expired_token_returns_401(self, jwks_server):
        provider = self._provider(jwks_server)
        token = _sign(jwks_server, self._claims(exp=int(time.time()) - 3600))
        body, status = provider.validate(f"Bearer {token}")
        assert status == 401

    def test_wrong_audience_returns_401(self, jwks_server):
        provider = self._provider(jwks_server)
        token = _sign(jwks_server, self._claims(aud="other-audience"))
        body, status = provider.validate(f"Bearer {token}")
        assert status == 401

    def test_wrong_issuer_returns_401(self, jwks_server):
        provider = self._provider(jwks_server)
        token = _sign(jwks_server, self._claims(iss="https://evil.example.com"))
        body, status = provider.validate(f"Bearer {token}")
        assert status == 401

    def test_tampered_signature_returns_401(self, jwks_server):
        provider = self._provider(jwks_server)
        token = _sign(jwks_server, self._claims())
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        body, status = provider.validate(f"Bearer {tampered}")
        assert status == 401

    def test_garbage_token_returns_401(self, jwks_server):
        provider = self._provider(jwks_server)
        body, status = provider.validate("Bearer not-a-jwt")
        assert status == 401


# ---------------------------------------------------------------------------
# _extract_bearer
# ---------------------------------------------------------------------------

class TestExtractBearer:

    def test_strips_prefix(self):
        assert _extract_bearer("Bearer abc") == "abc"

    def test_passthrough_without_prefix(self):
        assert _extract_bearer("abc") == "abc"


# ---------------------------------------------------------------------------
# build_auth_provider — fail-closed config wiring
# ---------------------------------------------------------------------------

class _FakeModel:
    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)


class TestBuildAuthProvider:

    def test_static_mode_returns_none(self):
        assert build_auth_provider(_FakeModel(auth_mode="static")) is None

    def test_missing_auth_mode_returns_none(self):
        assert build_auth_provider(_FakeModel()) is None

    def test_oauth2_without_jwks_url_returns_none(self):
        model = _FakeModel(auth_mode="oauth2", oauth2_jwks_url="")
        assert build_auth_provider(model) is None

    def test_oauth2_with_jwks_url_builds_provider(self, jwks_server):
        model = _FakeModel(
            auth_mode="oauth2",
            oauth2_jwks_url=jwks_server["url"],
            oauth2_audience="petp",
            oauth2_issuer="https://idp.example.com",
        )
        provider = build_auth_provider(model)
        assert provider is not None
        claims = {
            "aud": "petp",
            "iss": "https://idp.example.com",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        }
        assert provider.validate(f"Bearer {_sign(jwks_server, claims)}") is None
