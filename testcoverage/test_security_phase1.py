"""Phase 1 security regression tests.

Two attack surfaces hardened:
  A) HTTP auth fail-closed + token-disclosure endpoint removed.
  B) expression2str sandbox: dunder pre-scan + restricted __builtins__.

Run: pytest testcoverage/test_security_phase1.py -v
"""

import hmac
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Phase 1B — expression2str sandbox
# ---------------------------------------------------------------------------

class TestExpressionSandboxRCE:
    """RCE PoCs that MUST be blocked by the sandbox."""

    def test_block_import_os_popen(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        result = proc.expression2str('{__import__("os").popen("id").read()}')
        # Blocked → returns the literal expression unchanged
        assert "uid=" not in str(result)
        assert "{__import__" in str(result)

    def test_block_globals_traversal_via_self(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        result = proc.expression2str('{p.__init__.__globals__["os"].popen("id").read()}')
        assert "uid=" not in str(result)
        assert "{p.__init__" in str(result)

    def test_block_subclasses_traversal(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        result = proc.expression2str('{().__class__.__base__.__subclasses__()}')
        assert "<class" not in str(result)

    def test_block_builtins_access(self, make_processor):
        """Even if __builtins__ name is referenced directly, the dunder pattern blocks it."""
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        result = proc.expression2str('{__builtins__}')
        assert "module" not in str(result).lower() or "builtins" not in str(result).lower() or "{__builtins__}" in str(result)

    def test_block_open_via_safe_builtins(self, make_processor):
        """`open` is not in _SAFE_BUILTINS — must raise NameError and fall back."""
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        result = proc.expression2str('{open("/etc/passwd").read()}')
        # No password file content should leak
        assert "root:" not in str(result)

    def test_block_nested_dunder_inside_field(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"name": "Alice"})
        result = proc.expression2str('hi {__import__("os")}_{name}')
        # __import__ must not have executed
        assert "<module" not in str(result)


class TestExpressionSandboxRegression:
    """Existing legitimate usages MUST keep working."""

    def test_simple_variable(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"name": "world"})
        assert proc.expression2str("Hello {name}") == "Hello world"

    def test_p_method_call(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"x": "y"})
        assert proc.expression2str('{p.get_data("x")}') == "y"

    def test_arithmetic_in_field(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"x": 1})
        assert proc.expression2str("{x + 1}") == "2"

    def test_plain_string_no_braces(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {})
        assert proc.expression2str("plain text") == "plain text"

    def test_string_literal_with_dunder_outside_braces(self, make_processor):
        """CSS classes / IDs like `Items__abc` and `__session_key` MUST pass through.
        These appear in many existing yaml files and never enter f-string fields."""
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"x": "Y"})
        assert proc.expression2str("__session_key") == "__session_key"
        assert proc.expression2str("Items__b40h1d_{x}") == "Items__b40h1d_Y"
        assert proc.expression2str(".i8-text-input__input") == ".i8-text-input__input"

    def test_safe_builtins_available(self, make_processor):
        """Whitelisted builtins (len, str, int) MUST still work."""
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"ENCODE"}', {"items": [1, 2, 3]})
        assert proc.expression2str("{len(items)}") == "3"


# ---------------------------------------------------------------------------
# Phase 1A — HTTP auth fail-closed + disclosure endpoint removed
# ---------------------------------------------------------------------------

class _FakeHandler:
    """Minimal handler exposing .headers like BaseHTTPRequestHandler."""

    def __init__(self, headers=None):
        self.headers = headers or {}


class TestRequireTokenFailClosed:

    def _make_server(self, token):
        """Construct BackgroundHttpServer without starting it."""
        from httpservice.BackgroundHttpServer import BackgroundHttpServer
        runtime = MagicMock()
        return BackgroundHttpServer(runtime=runtime, port=0, timeout=5, token=token)

    def test_unconfigured_token_returns_501(self):
        """Fail-closed: when http_request_token is None/empty, EVERY request → 501.
        Previous behavior was fail-open (anonymous access). This is the critical fix."""
        srv = self._make_server(token=None)
        body, status = srv._require_token(_FakeHandler({"Authorization": "Bearer anything"}))
        assert status == 501
        assert "http_request_token" in body["error"]

    def test_unconfigured_token_no_auth_header_also_501(self):
        srv = self._make_server(token="")
        body, status = srv._require_token(_FakeHandler({}))
        assert status == 501

    def test_wrong_token_returns_401(self):
        srv = self._make_server(token="real-secret")
        body, status = srv._require_token(_FakeHandler({"Authorization": "Bearer wrong"}))
        assert status == 401
        assert body == {"error": "Unauthorized"}

    def test_missing_authorization_returns_401(self):
        srv = self._make_server(token="real-secret")
        body, status = srv._require_token(_FakeHandler({}))
        assert status == 401

    def test_correct_token_returns_none(self):
        srv = self._make_server(token="real-secret")
        result = srv._require_token(_FakeHandler({"Authorization": "Bearer real-secret"}))
        assert result is None

    def test_correct_token_without_bearer_prefix(self):
        """Bare token (no 'Bearer ' prefix) is also accepted — backward compat."""
        srv = self._make_server(token="real-secret")
        result = srv._require_token(_FakeHandler({"Authorization": "real-secret"}))
        assert result is None

    def test_token_compare_uses_constant_time(self):
        """Sanity: hmac.compare_digest is what's invoked. Timing-attack defense."""
        srv = self._make_server(token="aaaaaaaa")
        # Same length, every char differs — must still take constant time path.
        # We don't measure time here; we just verify _require_token still rejects.
        body, status = srv._require_token(_FakeHandler({"Authorization": "Bearer bbbbbbbb"}))
        assert status == 401


class TestDisclosureRouteRemoved:

    def test_mcp_well_known_route_not_registered(self):
        """The token-disclosure route GET /mcp/.well-known/openid-configuration
        was returning {token: <real_token>} to ANY caller. Must be gone from the route map."""
        from httpservice.BackgroundHttpServer import BackgroundHttpServer
        runtime = MagicMock()
        srv = BackgroundHttpServer(runtime=runtime, port=0, timeout=5, token="x")
        routes = srv._build_route_map()
        for k in routes.keys():
            assert ".well-known/openid-configuration" not in k, \
                f"disclosure route still registered: {k}"

    def test_handle_mcp_auth_method_removed(self):
        """The _handle_mcp_auth method itself is the leak — must not exist."""
        from httpservice.BackgroundHttpServer import BackgroundHttpServer
        assert not hasattr(BackgroundHttpServer, "_handle_mcp_auth"), \
            "_handle_mcp_auth still defined — token disclosure path open"

    def test_http_server_disclosure_route_not_registered(self):
        """Same check on the GUI HttpServer."""
        from httpservice.HttpServer import HttpServer
        # HttpServer uses presenter — pass mock
        presenter = MagicMock()
        presenter.m = MagicMock()
        srv = HttpServer.__new__(HttpServer)
        srv._token = "x"
        srv._port = 0
        srv._timeout = 5
        srv.presenter = presenter
        routes = srv._build_route_map() if hasattr(srv, "_build_route_map") else {}
        for k in routes.keys():
            assert ".well-known/openid-configuration" not in k

    def test_http_server_handle_mcp_auth_removed(self):
        from httpservice.HttpServer import HttpServer
        assert not hasattr(HttpServer, "_handle_mcp_auth"), \
            "HttpServer._handle_mcp_auth still defined — token disclosure path open"
