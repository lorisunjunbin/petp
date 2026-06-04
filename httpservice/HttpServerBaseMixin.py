import hmac
import logging
import time
from typing import Any, Optional

from httpservice.handlers.HttpRequestHandler import HttpRequestHandler


class HttpServerBaseMixin:
    """REST-layer shared logic, extracted from ``HttpServer`` / ``BackgroundHttpServer``.

    Covers stateless handlers that are identical across GUI and Background modes:
      - ``_require_token``         bearer token validation, fail-closed
      - ``_handle_health``         health check
      - ``_handle_mcp_get``        MCP GET (no server-initiated notifications → 204)
      - ``_status_code_for_result`` map result's ``ok`` field to HTTP status

    Requirement: subclasses must expose ``self._token: Optional[str]``.
    """

    def _require_token(self, handler: HttpRequestHandler) -> Optional[tuple]:
        """Validate the bearer token.

        Returns ``None`` on success, or an ``(error_dict, status_code)``
        tuple on rejection.

        Fail-closed semantics: when ``http_request_token`` is not
        configured the server refuses every authenticated request with
        501. This prevents a fail-open mode where empty token == public
        RCE on /petp/exec.
        """
        if not self._token:
            return ({"error": "Server requires http_request_token to be configured"}, 501)
        given = handler.headers.get("Authorization", "")
        prefix = "Bearer "
        if given.startswith(prefix):
            given = given[len(prefix):]
        if not hmac.compare_digest(given, self._token):
            return ({"error": "Unauthorized"}, 401)
        return None

    def _handle_health(self, handler: HttpRequestHandler, params: Optional[dict] = None) -> dict:
        """Health-check endpoint returning ``{"status": "ok", "timestamp": ...}``."""
        logging.debug("_handle_health params: %s", params)
        return {"status": "ok", "timestamp": time.time()}

    def _handle_mcp_get(self, handler: HttpRequestHandler, params: Optional[dict] = None):
        """Handle GET /mcp — SSE stream for server-initiated notifications.

        PETP does not push notifications, so return 204 No Content per MCP spec.
        """
        err = self._require_token(handler)
        if err is not None:
            return err
        return {}, 204

    @staticmethod
    def _status_code_for_result(result: Any) -> int:
        """Map a runtime result dict's ``ok`` field to HTTP status (200 / 500)."""
        if isinstance(result, dict) and "ok" in result:
            return 200 if bool(result.get("ok")) else 500
        return 200
