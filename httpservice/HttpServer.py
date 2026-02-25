import logging
import threading
import time
import json
import uuid
from http.server import ThreadingHTTPServer
import weakref
from collections import OrderedDict

import wx

from decorators.decorators import reload_http_log_after
from httpservice.handlers.HttpRequestHandler import HttpRequestHandler, StreamingResponseData
from mvp.presenter import PETPPresenter
from mvp.presenter.event.PETPEvent import PETPEvent


class HttpServer:
    # Maximum number of results to store in memory
    MAX_RESULTS_CACHE = 1000
    # Default cleanup interval in seconds
    CLEANUP_INTERVAL = 60

    def __init__(self, p: PETPPresenter):
        """Initialize the HTTP server with a presenter and default configuration

        Args:
            p: PETP Presenter instance
        """
        self.port = int(p.m.http_port)
        self.http_request_timeout = int(p.m.http_request_timeout)
        self.host = ""  # Empty string means listen on all available interfaces
        self.p = p
        self.httpd = None
        self._running = False

        # Use OrderedDict for FIFO behavior when cleaning up old results
        self._result_store = OrderedDict()
        self._result_events = weakref.WeakValueDictionary()  # Use weak references to avoid memory leaks
        self._result_lock = threading.RLock()  # Use reentrant lock for safer nested locking
        self._result_timestamps = {}  # Track when results were added

        # Start cleanup thread
        self._stop_cleanup = threading.Event()
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired_results, daemon=True)
        self._cleanup_thread.start()

        # Register the presenter's view
        HttpRequestHandler.register_view(p.v)

        # Register the server instance for result handling
        HttpRequestHandler.register_server(self)

        # Register default routes
        HttpRequestHandler.register_routes({
            'GET:/': self._handle_index,
            'GET:/health': self._handle_health,
            'GET:/petp/tools': self._handle_petp_tools,
            'POST:/petp/exec': self._handle_petp_event,
            'GET:/petp/result': self._handle_result_check,
            'GET:/mcp': self._handle_mcp,
            'POST:/mcp': self._handle_mcp,
            'DELETE:/mcp': self._handle_mcp
        })

    def _handle_index(self, handler, params=None):
        logging.debug(f"_handle_index params: {params}")

        return {
            "server": "PETP HTTP Server",
            "available_endpoints": [
                {
                    "description": "Check server status",
                    "uri": "/health",
                    "method": "GET"
                },
                {
                    "description": "Check server status",
                    "uri": "/health",
                    "method": "GET"
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
                            "fromHTTPService": "true"
                        }
                    }
                },
                {
                    "description": "To find available tools.",
                    "uri": "/petp/tools",
                    "method": "GET"
                },
                {
                    "description": "To find available tools.",
                    "uri": "/petp/result?request_id={request_id return from /exec with wait_for_result=false}",
                    "method": "GET"
                }
            ]
        }

    @reload_http_log_after
    def _handle_health(self, handler, params=None):
        logging.debug(f"_handle_health params: {params}")
        """Health check endpoint"""
        return {
            "status": "ok",
            "timestamp": time.time()
        }

    @reload_http_log_after
    def _handle_petp_tools(self, handler, payload) -> dict:
        logging.debug(f"_handle_petp_tools payload: {payload}")
        """Handle PETP event requests"""
        return self.p.get_tools()

    @reload_http_log_after
    def _handle_mcp(self, handler, params=None):
        """
        Entry point for PETP streaming transport,
        simulate standard MCP server(TransportType=HTTP Streaming).
        Delegates by JSON body "method" to dedicated handlers.
        """
        params = params or {}
        method = params.get('method')

        if not method:
            return {"info": "PETP MCP Server"}, 200

        dispatch = {
            'initialize': self._mcp_initialize,
            'notifications/initialized': self._mcp_initialized,
            'tools/list': self._mcp_tools_list,
            'tools/call': self._mcp_tools_call
        }

        handler_fn = dispatch.get(method)
        if handler_fn:
            return handler_fn(handler, params)

        return {"error": f"Unsupported method: {method}"}, 400

    # NOT-IN-USE
    def _mcp_legacy_stream(self, params):
        """Simple text stream kept for legacy clients without MCP method."""

        def legacy_stream():
            msg = params.get('message', 'hello')
            for i in range(1, 4):
                yield f"Processing file {i}/3...\n"
                time.sleep(1)
            yield f"Here's the file content: {msg}\n"

        return legacy_stream()

    def _mcp_initialize(self, handler, params):
        """Handle MCP initialize: respond with capabilities as SSE once."""
        request_id = params.get('id')
        # Generate a new 64-character session ID
        session_id = uuid.uuid4().hex + uuid.uuid4().hex
        protocol_version = handler.headers.get('mcp-protocol-version') or "2025-11-25"

        resp = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": protocol_version,
                "capabilities": {
                    "experimental": {},
                    "prompts": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                    "tools": {"listChanged": False}
                },
                "serverInfo": {"name": "PETP MCP server", "version": "1.0.0"}
            }
        }

        gen = (self._sse_event(resp) for _ in [0])
        return StreamingResponseData(gen, self._build_sse_headers(session_id), content_type='text/event-stream')

    def _mcp_initialized(self, handler, params):
        """Handle notifications/initialized acknowledgement."""
        session_id = self._extract_session_id(handler)
        gen = (self._sse_event({}) for _ in [0])
        return StreamingResponseData(gen, self._build_sse_headers(session_id), content_type='text/event-stream',
                                     status_code=202)

    def _mcp_tools_call(self, handler, payload):
        """Handle tools/call: stream progress then final result."""
        request_id = payload.get('id')
        session_id = self._extract_session_id(handler)
        action = payload.get('params', {}).get('name', '')
        params = payload.get('params', {}).get('arguments', {})
        message = params.get('message') or ''
        paramsInStr = json.dumps(params)

        def gen_call_result():
            # event: message
            # data: {"method": "notifications/message", "params": {"level": "info", "data": "calculate 1 + 2 = ?"},
            #        "jsonrpc": "2.0"}
            questionInfo = f"call tool: {action} with params: {paramsInStr}"

            if len(message) > 0:
                questionInfo += f", message: {message}"

            yield self._sse_event({
                "jsonrpc": "2.0",
                "method": "notifications/message",
                "params": {"level": "info", "data": questionInfo}
            })
            # event: message
            # data: {"jsonrpc": "2.0", "id": 1,
            #        "result": {"content": [{"type": "text", "text": "3"}], "structuredContent": {"result": 3}, "isError": false}}

            petpParam = {'execution': action}
            petpParam.update(params)
            result = self._handle_petp_event(handler, {
                'action': 'execution',
                'params': petpParam
            })

            yield self._sse_event({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": f" {questionInfo} -> {result}"
                    }],
                    "structuredContent": {
                        "type": "text",
                        "text": result,
                        "annotations": None,
                        "_meta": None
                    },
                    "isError": False
                }
            })

        return StreamingResponseData(gen_call_result(), self._build_sse_headers(session_id), 'text/event-stream')

    def _mcp_tools_list(self, handler, params):
        """Handle tools/list: return tools once as SSE message."""
        request_id = params.get('id')
        session_id = self._extract_session_id(handler)
        tools_payload = self._normalize_tools(self.p.get_tools())
        resp = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools_payload
            }
        }
        logging.info("PETP MCP Tools: %s", json.dumps(resp))
        gen = (self._sse_event(resp) for _ in [0])
        return StreamingResponseData(gen, self._build_sse_headers(session_id), content_type='text/event-stream')

    def _extract_session_id(self, handler):
        """Best-effort grab of MCP session id from headers."""
        return handler.headers.get('mcp-session-id') or handler.headers.get('MCP-Session-Id') or handler.headers.get(
            'Mcp-Session-Id')

    def _sse_event(self, payload: dict):
        """Wrap payload as SSE chunk (event: message)."""
        return f"event: message\ndata: {json.dumps(payload)}\n\n"
        # return json.dumps(payload)

    def _build_sse_headers(self, session_id):
        """Return SSE-friendly headers, echoing session id if provided."""
        headers = {
            'Cache-Control': 'no-cache, no-transform',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
            'content-type': 'text/event-stream',
            'x-accel-buffering': 'no',
            'transfer-encoding': 'chunked'
        }
        if session_id:
            headers['mcp-session-id'] = session_id
        return headers

    def _normalize_tools(self, tools_petp):
        """Ensure tools payload is a list per MCP spec.

        - If dict, convert to [{"name": key, "description": str(value)}].
        - Otherwise, wrap into empty list to avoid validation errors.
        """

        if isinstance(tools_petp, dict):
            result = []
            for k, v in tools_petp.items():
                tool = {"name": k}
                desc = self._prepareDescription(k, v)
                if desc:
                    tool["description"] = desc
                input_schema = self._prepareInputSchema(k, v)
                if input_schema:
                    tool["inputSchema"] = input_schema
                output_schema = self._prepareOutputSchema(k, v)
                if output_schema:
                    tool["outputSchema"] = output_schema
                result.append(tool)
            return result
        return []

    @staticmethod
    def _parse_tool_value(value) -> dict:
        """Convert tool value to dict, handling Chinese quotation marks.

        Args:
            value: Can be a JSON string (possibly with Chinese quotes), dict, or other type

        Returns:
            dict: Parsed dictionary, empty dict if parsing fails
        """
        if isinstance(value, dict):
            return value

        if not isinstance(value, str) or not value.strip():
            return {}

        # Replace Chinese quotation marks with ASCII ones
        normalized = (value.replace('“', '"')
                      .replace('”', '"')
                      .replace('\n', '')
                      .replace('：', ':'))
        try:
            return json.loads(normalized)
        except json.JSONDecodeError as ex:
            logging.error(ex)
            return {}

    def _prepareDescription(self, key: str, value: str) -> str:
        val: dict = self._parse_tool_value(value)
        return key if val.get('desc') is None else val.get('desc')

    def _prepareInputSchema(self, key, value) -> dict:
        val: dict = self._parse_tool_value(value)
        if val.get('inputSchema'):
            return val.get('inputSchema')

        if 'params' in val:
            params = val.get('params')
            if isinstance(params, list):
                # filter out empty str from params
                params = [p for p in params if p and isinstance(p, str) and p.strip()]
                props: dict = {p: {'title': p, 'type': 'string'} for p in params}
                return {
                    "title": f"{key}Arguments",
                    "type": "object",
                    "properties": props,
                    "required": params
                }

    def _prepareOutputSchema(self, key, value) -> dict:
        val: dict = self._parse_tool_value(value)
        if val.get('outputSchema'):
            return val.get('outputSchema')

        if 'outParams' in val:
            outParams: dict = val.get('outParams')
            if isinstance(outParams, list):
                outParams = [p for p in outParams if p and isinstance(p, str) and p.strip()]
                outProps: dict = {p: {'title': p, 'type': 'string'} for p in outParams}
                return {
                    "title": f"{key}Output",
                    "properties": outProps,
                    "required": outParams
                }

    @reload_http_log_after
    def _handle_petp_event(self, handler, payload):
        logging.debug(f"_handle_petp_event payload: {payload}")

        """Handle PETP event requests"""
        if not payload or 'action' not in payload or 'params' not in payload:
            return {"error": "Missing required 'action' or 'params' parameter"}, 400

        # Extract wait_for_result parameter (default: True for backward compatibility)
        wait_for_result = payload.get('wait_for_result', True)
        if not isinstance(wait_for_result, bool):
            wait_for_result = str(wait_for_result).lower() == 'true'

        request_id = self._generate_request_id()
        payload['params'][HttpRequestHandler.get_request_id_key()] = request_id

        # Post event to the view (asynchronously)
        wx.PostEvent(HttpRequestHandler.get_view(), PETPEvent(PETPEvent.HTTP_REQUEST, payload))

        # If client doesn't want to wait, return the request ID immediately
        if not wait_for_result:
            return {
                "status": "pending",
                "request_id": request_id,
                "message": "Request is being processed. Use GET /petp/result/{request_id} to check status."
            }

        # Wait for the result with timeout (backward compatibility)
        result = self._get_and_remove_result(request_id, timeout=self.http_request_timeout)

        if result is None:
            return {"error": "Request timed out"}, 408

        return result

    def store_result(self, request_id, result):
        if not request_id:
            logging.warning("Attempted to store result with empty request_id")
            return

        try:
            with self._result_lock:
                # Enforce maximum cache size by removing oldest items if needed
                if len(self._result_store) >= self.MAX_RESULTS_CACHE:
                    # Remove oldest item (first item in OrderedDict)
                    oldest_key = next(iter(self._result_store))
                    del self._result_store[oldest_key]
                    if oldest_key in self._result_timestamps:
                        del self._result_timestamps[oldest_key]
                    logging.debug(f"Cache full: Removed oldest result: {oldest_key}")

                # Store the result and timestamp
                self._result_store[request_id] = result
                self._result_timestamps[request_id] = time.time()

                # Set event if waiting threads exist
                event = self._result_events.get(request_id)
                if event and not event.is_set():
                    event.set()
        except Exception as e:
            logging.error(f"Error storing result for request {request_id}: {str(e)}")

    def _generate_request_id(self):
        """Generate a unique request ID for tracking async operations"""
        return str(uuid.uuid4())

    def _get_and_remove_result(self, request_id, timeout=10):
        if not request_id:
            logging.error("Invalid request_id provided to _get_and_remove_result")
            return None

        event = None

        try:
            # Check if result already exists before creating an event
            with self._result_lock:
                if request_id in self._result_store:
                    result = self._result_store.pop(request_id, None)
                    if request_id in self._result_timestamps:
                        del self._result_timestamps[request_id]
                    logging.info(f"Result for request {request_id} was immediately available")
                    return result

                # Create event if it doesn't exist
                event = threading.Event()
                self._result_events[request_id] = event

            # Wait for the result outside the lock to reduce contention
            result_ready = event.wait(timeout)

            with self._result_lock:
                if not result_ready:
                    logging.warning(f"Request {request_id} timed out after {timeout} seconds")
                    return None

                # Get and clean up the result
                result = self._result_store.pop(request_id, None)
                if request_id in self._result_timestamps:
                    del self._result_timestamps[request_id]

                if result is not None:
                    logging.info(f"Http Response for request ID: {request_id}")
                    logging.debug(f"Result details: {result}")
                else:
                    logging.warning(f"Result was set but not found for request {request_id}")

                return result

        except Exception as e:
            logging.error(f"Error retrieving result for request {request_id}: {str(e)}")
            return None

    def _cleanup_expired_results(self):
        """Background thread to clean up expired results"""
        while not self._stop_cleanup.is_set():
            try:
                time.sleep(self.CLEANUP_INTERVAL)

                with self._result_lock:
                    current_time = time.time()
                    expired_requests = []

                    # Find expired results
                    for req_id, timestamp in list(self._result_timestamps.items()):
                        if current_time - timestamp > 2 * self.http_request_timeout:
                            expired_requests.append(req_id)

                    # Remove expired results
                    for req_id in expired_requests:
                        if req_id in self._result_store:
                            del self._result_store[req_id]
                        if req_id in self._result_timestamps:
                            del self._result_timestamps[req_id]

                    if expired_requests:
                        logging.info(f"Cleaned up {len(expired_requests)} expired results")

            except Exception as e:
                logging.error(f"Error in cleanup thread: {str(e)}")

    def start(self):
        if self._running:
            logging.warning("HTTP Server is already running")
            return
        try:
            handler = HttpRequestHandler
            self.httpd = ThreadingHTTPServer((self.host, self.port), handler)
            server_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
            server_thread.start()
            self._running = True
            logging.info(f"HTTP Server is serving at http://{self.host or 'localhost'}:{self.port}")
        except Exception as e:
            logging.error(f"Failed to start HTTP Server: {e}, so can not handle any http request by this instance.")
            self._running = False

    def stop(self):

        self._stop_cleanup.set()
        if self._cleanup_thread.is_alive():
            self._cleanup_thread.join(0.5)  # Wait briefly for the thread to exit

        # Clear all pending requests to avoid memory leaks
        with self._result_lock:
            self._result_store.clear()
            self._result_timestamps.clear()
        # Events will be cleared by GC due to WeakValueDictionary

        if self.httpd and self._running:
            self.httpd.shutdown()
            self._running = False
            logging.info("HTTP Server has been stopped.")

    def get_result(self, request_id, remove=True):

        if not request_id:
            return None

        try:
            with self._result_lock:
                if request_id not in self._result_store:
                    return None

                result = self._result_store[request_id]

                if remove:
                    del self._result_store[request_id]
                    if request_id in self._result_timestamps:
                        del self._result_timestamps[request_id]

                return result
        except Exception as e:
            logging.error(f"Error retrieving result for request {request_id}: {str(e)}")
            return None

    @reload_http_log_after
    def _handle_result_check(self, handler, params=None):
        """Handle result check requests"""
        logging.debug(f"_handle_result_check params: {params}")

        if not params or 'request_id' not in params:
            return {"error": "Missing request_id parameter"}, 400

        request_id = params['request_id']
        result = self.get_result(request_id)

        if result is None:
            # Check if this is a known request that's still processing
            with self._result_lock:
                if request_id in self._result_events:
                    return {
                        "status": "pending",
                        "request_id": request_id,
                        "message": "Request is still being processed"
                    }

            return {"error": "Request not found or expired"}, 404

        return result
