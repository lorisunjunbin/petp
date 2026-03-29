import json
import logging
import threading
import time
import uuid
import weakref
from collections import OrderedDict
from http.server import ThreadingHTTPServer
from typing import Any, Callable, Generator, Optional, Union

import wx

from decorators.decorators import reload_http_log_after
from httpservice.handlers.HttpRequestHandler import HttpRequestHandler, StreamingResponseData
from mvp.presenter import PETPPresenter
from mvp.presenter.event.PETPEvent import PETPEvent


class HttpServer:
    """Embedded HTTP server that exposes PETP executions as REST and MCP endpoints.

    Supports two API styles:
      - PETP REST API  (/petp/exec, /petp/tools, /petp/result)
      - MCP Streamable HTTP (/mcp) following the JSON-RPC 2.0 based MCP protocol.

    Results from asynchronous executions are stored in an in-memory LRU cache
    with background cleanup of expired entries.
    """

    # Maximum number of results to keep in the in-memory cache
    MAX_RESULTS_CACHE: int = 1000
    # Interval (seconds) between expired-result cleanup sweeps
    CLEANUP_INTERVAL: int = 60

    # ------------------------------------------------------------------
    # Construction & route registration
    # ------------------------------------------------------------------

    def __init__(self, presenter: PETPPresenter) -> None:
        """Initialize the HTTP server.

        Args:
            presenter: The PETP MVP presenter that drives business logic.
        """
        self.p: PETPPresenter = presenter  # Public — accessed by @reload_http_log_after decorator
        self._port: int = int(presenter.m.http_port)
        self._timeout: int = int(presenter.m.http_request_timeout)
        self._token: Optional[str] = presenter.m.http_request_token
        self._host: str = ""  # Empty string = listen on all interfaces
        self._httpd: Optional[ThreadingHTTPServer] = None
        self._running: bool = False

        # Ordered dict gives FIFO eviction when the cache is full
        self._result_store: OrderedDict[str, Any] = OrderedDict()
        # Weak refs avoid memory leaks: once no thread waits on an event it is GC'd
        self._result_events: weakref.WeakValueDictionary[str, threading.Event] = (
            weakref.WeakValueDictionary()
        )
        self._result_lock: threading.RLock = threading.RLock()
        self._result_timestamps: dict[str, float] = {}

        # Background sweeper for stale results
        self._stop_cleanup: threading.Event = threading.Event()
        self._cleanup_thread: threading.Thread = threading.Thread(
            target=self._cleanup_expired_results, daemon=True
        )
        self._cleanup_thread.start()

        # Wire handler to the presenter's view and to this server instance
        HttpRequestHandler.register_view(presenter.v)
        HttpRequestHandler.register_server(self)

        # Register REST + MCP routes
        HttpRequestHandler.register_routes(self._build_route_map())

    def _build_route_map(self) -> dict[str, Callable]:
        """Return the mapping from ``METHOD:path`` strings to handler callables."""
        return {
            "GET:/": self._handle_index,
            "GET:/health": self._handle_health,
            "GET:/petp/tools": self._handle_petp_tools,
            "POST:/petp/exec": self._handle_petp_event,
            "GET:/petp/result": self._handle_result_check,
            "GET:/mcp": self._handle_mcp,
            "POST:/mcp": self._handle_mcp,
            "DELETE:/mcp": self._handle_mcp,
            "GET:/mcp/.well-known/openid-configuration": self._handle_mcp_auth,
        }

    # ------------------------------------------------------------------
    # Index & health endpoints
    # ------------------------------------------------------------------

    def _handle_index(self, handler: HttpRequestHandler, params: Optional[dict] = None) -> dict:
        """Return a human-readable summary of available endpoints."""
        logging.debug("_handle_index params: %s", params)
        return {
            "server": "PETP HTTP Server",
            "available_endpoints": [
                {
                    "description": "Check server status",
                    "uri": "/health",
                    "method": "GET",
                },
                {
                    "description": "Trigger a PETP event - run get recent data from news.ceic.ac.cn",
                    "uri": "/petp/exec",
                    "method": "POST",
                    "payload": {
                        "wait_for_result": "true | false",
                        "action": "execution",
                        "params": {
                            "execution": "OOTB_BS4_GET_DATA_FROM_news.ceic.ac.cn",
                            "fromHTTPService": "true",
                        },
                    },
                },
                {
                    "description": "List available tools",
                    "uri": "/petp/tools",
                    "method": "GET",
                },
                {
                    "description": (
                        "Poll a previously submitted request. "
                        "Use the request_id returned by /exec when wait_for_result=false."
                    ),
                    "uri": "/petp/result?request_id={request_id}",
                    "method": "GET",
                },
                {
                    "description": "Standard MCP Streamable HTTP endpoint",
                    "uri": "/mcp",
                    "method": "GET | POST | DELETE",
                },
            ],
        }

    @reload_http_log_after
    def _handle_health(self, handler: HttpRequestHandler, params: Optional[dict] = None) -> dict:
        """Health-check endpoint returning ``{"status": "ok"}``."""
        logging.debug("_handle_health params: %s", params)
        return {"status": "ok", "timestamp": time.time()}

    # ------------------------------------------------------------------
    # PETP REST API
    # ------------------------------------------------------------------

    @reload_http_log_after
    def _handle_petp_tools(self, handler: HttpRequestHandler, payload: dict) -> dict:
        """Return the full list of PETP execution tools."""
        logging.debug("_handle_petp_tools payload: %s", payload)
        return self.p.get_tools()

    @reload_http_log_after
    def _handle_petp_event(
        self, handler: HttpRequestHandler, payload: Optional[dict]
    ) -> Union[dict, tuple]:
        """Execute a PETP event synchronously or asynchronously.

        If ``wait_for_result`` is *True* (default), the call blocks until the
        execution finishes or the timeout expires.  Otherwise a ``request_id``
        is returned immediately and the client can poll ``/petp/result``.
        """
        logging.debug("_handle_petp_event payload: %s", payload)

        if not payload or "action" not in payload or "params" not in payload:
            return {"error": "Missing required 'action' or 'params' parameter"}, 400

        # Normalize the wait_for_result flag
        wait_for_result = payload.get("wait_for_result", True)
        if not isinstance(wait_for_result, bool):
            wait_for_result = str(wait_for_result).lower() == "true"

        request_id: str = self._generate_request_id()
        payload["params"][HttpRequestHandler.get_request_id_key()] = request_id

        # Dispatch the event to the wxPython view (asynchronous execution)
        wx.PostEvent(
            HttpRequestHandler.get_view(),
            PETPEvent(PETPEvent.HTTP_REQUEST, payload),
        )

        # Fire-and-forget mode: return the request_id immediately
        if not wait_for_result:
            return {
                "status": "pending",
                "request_id": request_id,
                "message": "Request is being processed. Use GET /petp/result?request_id=<id> to check status.",
            }

        # Synchronous mode: block until the result arrives or times out
        result = self._get_and_remove_result(request_id, timeout=self._timeout)
        if result is None:
            return {"error": "Request timed out"}, 408

        return result

    @reload_http_log_after
    def _handle_result_check(
        self, handler: HttpRequestHandler, params: Optional[dict] = None
    ) -> Union[dict, tuple]:
        """Poll the result of a previously submitted asynchronous request."""
        logging.debug("_handle_result_check params: %s", params)

        if not params or "request_id" not in params:
            return {"error": "Missing request_id parameter"}, 400

        request_id: str = params["request_id"]
        result = self.get_result(request_id)

        if result is None:
            # Distinguish "still processing" from "unknown / expired"
            with self._result_lock:
                if request_id in self._result_events:
                    return {
                        "status": "pending",
                        "request_id": request_id,
                        "message": "Request is still being processed",
                    }
            return {"error": "Request not found or expired"}, 404

        return result

    # ------------------------------------------------------------------
    # MCP (Model Context Protocol) endpoints
    # ------------------------------------------------------------------

    @reload_http_log_after
    def _handle_mcp_auth(
        self, handler: HttpRequestHandler, params: Optional[dict] = None
    ) -> tuple:
        """Return the bearer token for MCP authentication discovery."""
        return {"token": self._token}, 200

    @reload_http_log_after
    def _handle_mcp(
        self, handler: HttpRequestHandler, params: Optional[dict] = None
    ) -> Union[dict, tuple, StreamingResponseData]:
        """Entry point for the MCP Streamable HTTP transport.

        Routes the request to a dedicated handler based on the ``method`` field
        in the JSON-RPC body.
        """
        params = params or {}
        method: Optional[str] = params.get("method")
        token: Optional[str] = handler.headers.get("Authorization")

        logging.info("_handle_mcp path: %s, method: %s", handler.path, method)

        # Token-based access control (skip when _token is None)
        if self._token is not None and token != f"Bearer {self._token}":
            return {"warning": "PETP Invalid token"}, 403

        if not method:
            return {"info": "PETP MCP Server"}, 200

        dispatch: dict[str, Callable] = {
            "initialize": self._mcp_initialize,
            "notifications/initialized": self._mcp_initialized,
            "tools/list": self._mcp_tools_list,
            "tools/call": self._mcp_tools_call,
            "prompts/list": self._mcp_prompts_list,
            "resources/list": self._mcp_resources_list,
            ".well-known/openid-configuration": self._mcp_initialize,
        }

        handler_fn: Optional[Callable] = dispatch.get(method)
        if handler_fn:
            return handler_fn(handler, params)

        logging.warning("_handle_mcp unsupported method: %s", method)
        return {"error": f"Unsupported method: {method}"}, 400

    # ---- MCP protocol handlers ----

    def _mcp_initialize(
        self, handler: HttpRequestHandler, params: dict
    ) -> StreamingResponseData:
        """Handle MCP ``initialize``: respond with server capabilities via SSE."""
        request_id = params.get("id")
        session_id: str = uuid.uuid4().hex + uuid.uuid4().hex  # 64-char session ID
        protocol_version: str = handler.headers.get("mcp-protocol-version") or "2025-11-25"

        resp = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": protocol_version,
                "capabilities": {
                    "experimental": {},
                    "prompts": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                    "tools": {"listChanged": False},
                },
                "serverInfo": {"name": "PETP MCP server", "version": "1.0.0"},
            },
        }

        return self._single_sse_response(resp, session_id)

    def _mcp_initialized(
        self, handler: HttpRequestHandler, params: dict
    ) -> StreamingResponseData:
        """Handle ``notifications/initialized`` acknowledgement (HTTP 202)."""
        session_id: Optional[str] = self._extract_session_id(handler)
        return StreamingResponseData(
            self._single_sse_chunk({}),
            self._build_sse_headers(session_id),
            content_type="text/event-stream",
            status_code=202,
        )

    def _mcp_tools_list(
        self, handler: HttpRequestHandler, params: dict
    ) -> StreamingResponseData:
        """Handle ``tools/list``: return available tools as a single SSE message."""
        request_id = params.get("id")
        session_id: Optional[str] = self._extract_session_id(handler)
        tools_payload: list[dict] = self._normalize_tools(self.p.get_tools())

        resp = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools_payload},
        }
        logging.info("PETP MCP Tools: %s", json.dumps(resp))

        return self._single_sse_response(resp, session_id)

    def _mcp_tools_call(
        self, handler: HttpRequestHandler, payload: dict
    ) -> StreamingResponseData:
        """Handle ``tools/call``: stream a progress notification then the final result."""
        request_id = payload.get("id")
        session_id: Optional[str] = self._extract_session_id(handler)
        action: str = payload.get("params", {}).get("name", "")
        arguments: dict = payload.get("params", {}).get("arguments", {})
        message: str = arguments.get("message") or ""
        arguments_json: str = json.dumps(arguments)

        def _stream_call_result() -> Generator[str, None, None]:
            """Yield SSE frames: first a progress notification, then the tool result."""
            question_info = f"call tool: {action} with params: {arguments_json}"
            if message:
                question_info += f", message: {message}"

            # Emit a progress / log notification
            yield self._sse_event({
                "jsonrpc": "2.0",
                "method": "notifications/message",
                "params": {"level": "info", "data": question_info},
            })

            # Execute the PETP event and emit the final result
            petp_param: dict = {"execution": action}
            petp_param.update(arguments)
            result = self._handle_petp_event(handler, {
                "action": "execution",
                "params": petp_param,
            })

            yield self._sse_event({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": f" {question_info} -> {result}"}],
                    "structuredContent": {
                        "type": "text",
                        "text": result,
                        "annotations": None,
                        "_meta": None,
                    },
                    "isError": False,
                },
            })

        return StreamingResponseData(
            _stream_call_result(),
            self._build_sse_headers(session_id),
            "text/event-stream",
        )

    def _mcp_prompts_list(
        self, handler: HttpRequestHandler, params: dict
    ) -> StreamingResponseData:
        """Handle ``prompts/list`` — currently returns an empty list."""
        request_id = params.get("id")
        session_id: Optional[str] = self._extract_session_id(handler)
        resp = {"jsonrpc": "2.0", "id": request_id, "result": {"prompts": []}}
        logging.info("PETP MCP prompts: %s", json.dumps(resp))
        return self._single_sse_response(resp, session_id)

    def _mcp_resources_list(
        self, handler: HttpRequestHandler, params: dict
    ) -> StreamingResponseData:
        """Handle ``resources/list`` — currently returns an empty list."""
        request_id = params.get("id")
        session_id: Optional[str] = self._extract_session_id(handler)
        resp = {"jsonrpc": "2.0", "id": request_id, "result": {"resources": []}}
        logging.info("PETP MCP resources: %s", json.dumps(resp))
        return self._single_sse_response(resp, session_id)

    # ------------------------------------------------------------------
    # SSE (Server-Sent Events) helpers
    # ------------------------------------------------------------------

    def _extract_session_id(self, handler: HttpRequestHandler) -> Optional[str]:
        """Best-effort retrieval of the MCP session ID from request headers."""
        return (
            handler.headers.get("mcp-session-id")
            or handler.headers.get("MCP-Session-Id")
            or handler.headers.get("Mcp-Session-Id")
        )

    def _sse_event(self, payload: dict) -> str:
        """Wrap a JSON payload as a single SSE ``event: message`` chunk."""
        return f"event: message\ndata: {json.dumps(payload)}\n\n"

    def _single_sse_chunk(self, payload: dict) -> Generator[str, None, None]:
        """Yield exactly one SSE chunk for *payload*."""
        yield self._sse_event(payload)

    def _single_sse_response(
        self, resp: dict, session_id: Optional[str]
    ) -> StreamingResponseData:
        """Build a ``StreamingResponseData`` that emits one SSE event."""
        return StreamingResponseData(
            self._single_sse_chunk(resp),
            self._build_sse_headers(session_id),
            content_type="text/event-stream",
        )

    def _build_sse_headers(self, session_id: Optional[str]) -> dict[str, str]:
        """Return standard SSE headers, echoing the session ID when present."""
        headers: dict[str, str] = {
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "Transfer-Encoding": "chunked",
            "X-Accel-Buffering": "no",
        }
        if session_id:
            headers["mcp-session-id"] = session_id
        return headers

    # ------------------------------------------------------------------
    # Tool normalization (PETP internal -> MCP tools/list schema)
    # ------------------------------------------------------------------

    def _normalize_tools(self, tools_petp: Any) -> list[dict]:
        """Convert the PETP tools dict into a list of MCP tool definitions.

        Each entry becomes ``{"name": key, "description": ..., "inputSchema": ..., "outputSchema": ...}``.

        Returns an empty list when *tools_petp* is not a dict.
        """
        if not isinstance(tools_petp, dict):
            return []

        result: list[dict] = []
        for key, value in tools_petp.items():
            tool: dict = {"name": key}
            parsed: dict = self._parse_tool_value(value)

            desc = self._extract_description(key, parsed)
            if desc:
                tool["description"] = desc

            input_schema = self._build_input_schema(key, parsed)
            if input_schema:
                tool["inputSchema"] = input_schema

            output_schema = self._build_output_schema(key, parsed)
            if output_schema:
                tool["outputSchema"] = output_schema

            result.append(tool)
        return result

    @staticmethod
    def _parse_tool_value(value: Any) -> dict:
        """Parse a tool's raw value into a dict.

        Handles dicts, JSON strings (including those with Chinese quotation marks),
        and gracefully returns an empty dict on failure.
        """
        if isinstance(value, dict):
            return value
        if not isinstance(value, str) or not value.strip():
            return {}

        # Normalize Chinese punctuation to ASCII equivalents
        normalized: str = (
            value.replace("\u201c", '"')   # left double quotation mark
            .replace("\u201d", '"')        # right double quotation mark
            .replace("\n", "")
            .replace("\uff1a", ":")        # fullwidth colon
        )
        try:
            return json.loads(normalized)
        except json.JSONDecodeError:
            logging.exception("Failed to parse tool value")
            return {}

    @staticmethod
    def _extract_description(key: str, parsed: dict) -> Optional[str]:
        """Return the tool description, falling back to *key*."""
        return key if parsed.get("desc") is None else parsed.get("desc")

    @staticmethod
    def _build_input_schema(key: str, parsed: dict) -> Optional[dict]:
        """Build an ``inputSchema`` from explicit schema or a flat ``params`` list."""
        if parsed.get("inputSchema"):
            return parsed["inputSchema"]

        params = parsed.get("params")
        if isinstance(params, list):
            # Filter out empty / blank entries
            clean_params: list[str] = [
                p for p in params if isinstance(p, str) and p.strip()
            ]
            properties: dict = {p: {"title": p, "type": "string"} for p in clean_params}
            return {
                "title": f"{key}Arguments",
                "type": "object",
                "properties": properties,
                "required": clean_params,
            }
        return None

    @staticmethod
    def _build_output_schema(key: str, parsed: dict) -> Optional[dict]:
        """Build an ``outputSchema`` from explicit schema or a flat ``outParams`` list."""
        if parsed.get("outputSchema"):
            return parsed["outputSchema"]

        out_params = parsed.get("outParams")
        if isinstance(out_params, list):
            clean_params: list[str] = [
                p for p in out_params if isinstance(p, str) and p.strip()
            ]
            properties: dict = {p: {"title": p, "type": "string"} for p in clean_params}
            return {
                "title": f"{key}Output",
                "properties": properties,
                "required": clean_params,
            }
        return None

    # ------------------------------------------------------------------
    # Result store (async execution support)
    # ------------------------------------------------------------------

    def store_result(self, request_id: str, result: Any) -> None:
        """Store an execution result so a waiting client can retrieve it."""
        if not request_id:
            logging.warning("Attempted to store result with empty request_id")
            return

        try:
            with self._result_lock:
                # Evict the oldest entry when the cache is full
                if len(self._result_store) >= self.MAX_RESULTS_CACHE:
                    oldest_key: str = next(iter(self._result_store))
                    del self._result_store[oldest_key]
                    self._result_timestamps.pop(oldest_key, None)
                    logging.debug("Cache full — evicted oldest result: %s", oldest_key)

                self._result_store[request_id] = result
                self._result_timestamps[request_id] = time.time()

                # Wake up any thread that is blocked waiting for this result
                event = self._result_events.get(request_id)
                if event and not event.is_set():
                    event.set()
        except Exception:
            logging.exception("Error storing result for request %s", request_id)

    def get_result(self, request_id: str, remove: bool = True) -> Any:
        """Retrieve a stored result by *request_id*.

        Args:
            request_id: The unique identifier of the request.
            remove: If *True*, delete the result from the store after reading.

        Returns:
            The stored result, or ``None`` if not found.
        """
        if not request_id:
            return None

        try:
            with self._result_lock:
                if request_id not in self._result_store:
                    return None

                result = self._result_store[request_id]
                if remove:
                    del self._result_store[request_id]
                    self._result_timestamps.pop(request_id, None)
                return result
        except Exception:
            logging.exception("Error retrieving result for request %s", request_id)
            return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_request_id() -> str:
        """Generate a unique request ID (UUID4)."""
        return str(uuid.uuid4())

    def _get_and_remove_result(self, request_id: str, timeout: int = 10) -> Any:
        """Block until the result for *request_id* is available or *timeout* elapses.

        The result is removed from the store once consumed.
        """
        if not request_id:
            logging.error("Invalid request_id provided to _get_and_remove_result")
            return None

        try:
            # Fast path: result is already available
            with self._result_lock:
                if request_id in self._result_store:
                    result = self._result_store.pop(request_id, None)
                    self._result_timestamps.pop(request_id, None)
                    logging.info("Result for request %s was immediately available", request_id)
                    return result

                # Register an event so the producer can wake us up
                event = threading.Event()
                self._result_events[request_id] = event

            # Wait outside the lock to reduce contention
            result_ready: bool = event.wait(timeout)

            with self._result_lock:
                if not result_ready:
                    logging.warning("Request %s timed out after %s seconds", request_id, timeout)
                    return None

                result = self._result_store.pop(request_id, None)
                self._result_timestamps.pop(request_id, None)

                if result is not None:
                    logging.info("Http Response for request ID: %s", request_id)
                    logging.debug("Result details: %s", result)
                else:
                    logging.warning("Result was set but not found for request %s", request_id)

                return result
        except Exception:
            logging.exception("Error retrieving result for request %s", request_id)
            return None

    def _cleanup_expired_results(self) -> None:
        """Background thread that periodically evicts stale results.

        A result is considered expired when its age exceeds twice the configured
        request timeout.
        """
        while not self._stop_cleanup.is_set():
            try:
                self._stop_cleanup.wait(self.CLEANUP_INTERVAL)
                if self._stop_cleanup.is_set():
                    break

                with self._result_lock:
                    now: float = time.time()
                    max_age: float = 2 * self._timeout
                    expired: list[str] = [
                        req_id
                        for req_id, ts in self._result_timestamps.items()
                        if now - ts > max_age
                    ]

                    for req_id in expired:
                        self._result_store.pop(req_id, None)
                        del self._result_timestamps[req_id]

                    if expired:
                        logging.info("Cleaned up %d expired results", len(expired))
            except Exception:
                logging.exception("Error in cleanup thread")

    # ------------------------------------------------------------------
    # Server lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the HTTP server on the configured host:port."""
        if self._running:
            logging.warning("HTTP Server is already running")
            return

        try:
            self._httpd = ThreadingHTTPServer((self._host, self._port), HttpRequestHandler)
            server_thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
            server_thread.start()
            self._running = True
            logging.info(
                "HTTP Server is serving at http://%s:%d",
                self._host or "localhost",
                self._port,
            )
        except Exception:
            logging.exception(
                "Failed to start HTTP Server — no HTTP requests will be handled by this instance."
            )
            self._running = False

    def stop(self) -> None:
        """Shut down the HTTP server and release all resources."""
        # Signal the cleanup thread to exit and wait briefly
        self._stop_cleanup.set()
        if self._cleanup_thread.is_alive():
            self._cleanup_thread.join(0.5)

        # Clear all pending results (events are GC'd via WeakValueDictionary)
        with self._result_lock:
            self._result_store.clear()
            self._result_timestamps.clear()

        if self._httpd and self._running:
            self._httpd.shutdown()
            self._running = False
            logging.info("HTTP Server has been stopped.")