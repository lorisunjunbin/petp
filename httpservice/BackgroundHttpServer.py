import json
import logging
import threading
import time
import uuid
import weakref
from collections import OrderedDict
from http.server import ThreadingHTTPServer
from typing import Any, Callable, Generator, Optional, Union, cast

from core.runtime.BackgroundRuntime import BackgroundRuntime
from httpservice.McpMixin import McpMixin
from httpservice.handlers.HttpRequestHandler import HttpRequestHandler, StreamingResponseData


class BackgroundHttpServer(McpMixin):
    MAX_RESULTS_CACHE: int = 1000

    def __init__(self, runtime: BackgroundRuntime, port: int, timeout: int, token: Optional[str] = None) -> None:
        self.runtime = runtime
        self._port = int(port)
        self._timeout = int(timeout)
        self._token = token
        self._host = ""
        self._httpd: Optional[ThreadingHTTPServer] = None
        self._running = False

        self._result_store: OrderedDict[str, Any] = OrderedDict()
        self._result_events: weakref.WeakValueDictionary[str, threading.Event] = weakref.WeakValueDictionary()
        self._result_lock: threading.RLock = threading.RLock()

        HttpRequestHandler.register_view(None)
        HttpRequestHandler.register_server(self)
        HttpRequestHandler.register_routes(self._build_route_map())

    def _build_route_map(self) -> dict[str, Callable]:
        return {
            "GET:/": self._handle_index,
            "GET:/health": self._handle_health,
            "GET:/petp/tools": self._handle_petp_tools,
            "POST:/petp/exec": self._handle_petp_exec,
            "GET:/petp/result": self._handle_result_check,
            "GET:/petp/crons": self._handle_cron_list,
            "GET:/petp/crons/history": self._handle_cron_history,
            "GET:/mcp": self._handle_mcp_get,
            "POST:/mcp": self._handle_mcp,
            "DELETE:/mcp": self._handle_mcp,
            "GET:/mcp/.well-known/openid-configuration": self._handle_mcp_auth,
        }

    def _handle_index(self, handler: HttpRequestHandler, params: Optional[dict] = None) -> dict:
        return {
            "server": "PETP Background HTTP Server",
            "available_endpoints": ["/health", "/petp/exec", "/petp/tools", "/petp/result", "/petp/crons",
                                    "/petp/crons/history", "/mcp"],
        }

    def _handle_health(self, handler: HttpRequestHandler, params: Optional[dict] = None) -> dict:
        return {"status": "ok", "timestamp": time.time()}

    def _handle_petp_tools(self, handler: HttpRequestHandler, payload: Optional[dict] = None) -> dict:
        return self.runtime.get_tools()

    def _handle_petp_exec(self, handler: HttpRequestHandler, payload: Optional[dict]) -> Union[dict, tuple]:
        if not payload or "action" not in payload or "params" not in payload:
            return {"error": "Missing required 'action' or 'params' parameter"}, 400

        action = payload.get("action", "execution")
        wait_for_result = payload.get("wait_for_result", True)
        if not isinstance(wait_for_result, bool):
            wait_for_result = str(wait_for_result).lower() == "true"

        params = payload.get("params", {})
        if not isinstance(params, dict):
            return {"error": "params must be a JSON object"}, 400

        request_id = self._generate_request_id()

        if action == "execution":
            execution_name = params.get("execution")
            if not isinstance(execution_name, str) or not execution_name:
                return {"error": "params.execution is required"}, 400
            exec_name: str = cast(str, execution_name)

            if wait_for_result:
                runtime_result = self.runtime.run_execution(exec_name, params)
                client_result = self._extract_business_response(runtime_result)
                return client_result, 200 if bool(runtime_result.get("ok")) else 500

            self._submit_async(request_id, lambda: self.runtime.run_execution(exec_name, params))
            return {
                "status": "pending",
                "request_id": request_id,
                "message": "Request is being processed. Use GET /petp/result?request_id=<id> to check status.",
            }, 202

        if action == "pipeline":
            pipeline_name = params.get("pipeline")
            if not isinstance(pipeline_name, str) or not pipeline_name:
                return {"error": "params.pipeline is required"}, 400
            pipe_name: str = cast(str, pipeline_name)

            if wait_for_result:
                runtime_result = self.runtime.run_pipeline(pipe_name, params)
                client_result = self._extract_business_response(runtime_result)
                return client_result, 200 if bool(runtime_result.get("ok")) else 500

            self._submit_async(request_id, lambda: self.runtime.run_pipeline(pipe_name, params))
            return {
                "status": "pending",
                "request_id": request_id,
                "message": "Request is being processed. Use GET /petp/result?request_id=<id> to check status.",
            }, 202

        return {"error": f"Unsupported action: {action}"}, 400

    def _handle_result_check(self, handler: HttpRequestHandler, params: Optional[dict] = None) -> Union[dict, tuple]:
        if not params or "request_id" not in params:
            return {"error": "Missing request_id parameter"}, 400

        request_id = params["request_id"]
        result = self.get_result(request_id)
        if result is None:
            with self._result_lock:
                if request_id in self._result_events:
                    return {
                        "status": "pending",
                        "request_id": request_id,
                        "message": "Request is still being processed",
                    }, 200
            return {"error": "Request not found or expired"}, 404
        return result, self._status_code_for_result(result)

    def _handle_cron_list(self, handler: HttpRequestHandler, params: Optional[dict] = None) -> dict:
        return {"crons": self.runtime.get_active_crons()}

    def _handle_cron_history(self, handler: HttpRequestHandler, params: Optional[dict] = None) -> Union[dict, tuple]:
        params = params or {}
        pipeline_name = params.get("pipeline")
        limit = int(params.get("limit", 50))
        record_id = params.get("id")

        if record_id:
            record = self.runtime.get_cron_record(record_id)
            if record is None:
                return {"error": "Record not found"}, 404
            return record

        return {"history": self.runtime.get_cron_history(pipeline_name, limit)}

    def _handle_mcp_auth(self, handler: HttpRequestHandler, params: Optional[dict] = None) -> tuple:
        return {"token": self._token}, 200

    def _handle_mcp_get(self, handler: HttpRequestHandler, params: Optional[dict] = None):
        """Handle GET /mcp — SSE stream for server-initiated notifications.
        PETP does not push notifications, so return 204 No Content per MCP spec."""
        token = handler.headers.get("Authorization")
        if self._token and token != f"Bearer {self._token}":
            return {"error": "Invalid token"}, 403
        return {}, 204

    def _handle_mcp(
            self,
            handler: HttpRequestHandler,
            params: Optional[dict] = None,
    ) -> Union[StreamingResponseData, tuple]:
        params = params or {}
        token = handler.headers.get("Authorization")
        if self._token and token != f"Bearer {self._token}":
            return {"error": "Invalid token"}, 403

        # Batch request support
        if '_batch' in params:
            return self._handle_mcp_batch(handler, params['_batch'], self._handle_mcp)

        session_id = self._extract_session_id(handler)
        method = params.get("method")

        if not method:
            return self._mcp_method_not_found(params.get("id"), "(empty)", session_id, handler)

        if method == "initialize":
            session_id = session_id or (uuid.uuid4().hex + uuid.uuid4().hex)
            protocol_version = params.get("params", {}).get("protocolVersion") or "2025-11-25"
            return self._mcp_initialize_response(params.get("id"), protocol_version, session_id, "PETP Background MCP", handler)

        if method == "notifications/initialized":
            return self._mcp_initialized_response(session_id)

        if method == "tools/list":
            return self._mcp_tools_list_response(params.get("id"), session_id, self.runtime.get_tools(), handler)

        if method == "tools/call":
            request_id = params.get("id")
            tool_name = params.get("params", {}).get("name")
            arguments = params.get("params", {}).get("arguments", {})
            if not isinstance(tool_name, str) or not tool_name:
                return self._single_sse_response({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32602, "message": "Invalid params: params.name is required"},
                }, session_id)
            tool_exec_name: str = cast(str, tool_name)
            arguments_json = json.dumps(arguments, ensure_ascii=False)
            info = f"call tool: {tool_exec_name} with params: {arguments_json}"
            logging.info("MCP tools/call: %s", info)

            if not self._wants_sse(handler):
                raw_result = self._run_with_timeout(
                    lambda: self.runtime.run_execution(tool_exec_name, arguments),
                    self._timeout,
                )
                return self._mcp_tools_call_json_response(
                    request_id, session_id, raw_result, tool_exec_name,
                    self.runtime.get_tools, handler,
                )

            def _stream_call_result() -> Generator[str, None, None]:
                yield self._sse_event({
                    "jsonrpc": "2.0",
                    "method": "notifications/message",
                    "params": {"level": "info", "data": info},
                })

                result = None
                for item in self._run_with_progress(
                    lambda: self.runtime.run_execution(tool_exec_name, arguments),
                    self._timeout, tool_exec_name,
                ):
                    if isinstance(item, str):
                        yield item
                    else:
                        result = item

                client_result, structured_content = self._build_tools_call_result(
                    tool_exec_name, result, self.runtime.get_tools
                )

                is_error = self._is_mcp_error_result(result)
                if is_error:
                    error_msg = structured_content.get("error", "unknown error") if isinstance(structured_content, dict) else "unknown error"
                    content_text = f"[{tool_exec_name}] error: {error_msg}"
                else:
                    content_text = self._to_mcp_text(structured_content)
                if isinstance(result, dict) and result.get("meta") is not None:
                    logging.info("MCP tools/call meta for %s: %s", tool_name,
                                 json.dumps(result.get("meta"), ensure_ascii=False, default=str))
                yield self._sse_event({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": content_text}],
                        "structuredContent": structured_content,
                        "isError": is_error,
                    },
                })

            return StreamingResponseData(_stream_call_result(), self._build_sse_headers(session_id),
                                         "text/event-stream", 200)

        return self._mcp_method_not_found(params.get("id"), method, session_id, handler)

    @staticmethod
    def _status_code_for_result(result: Any) -> int:
        if isinstance(result, dict) and "ok" in result:
            return 200 if bool(result.get("ok")) else 500
        return 200

    def _submit_async(self, request_id: str, task: Callable[[], dict]) -> None:
        event = threading.Event()
        with self._result_lock:
            self._result_events[request_id] = event

        def _runner():
            runtime_result = task()
            client_result = self._extract_business_response(runtime_result)
            self.store_result(request_id, client_result)

        threading.Thread(target=_runner, daemon=True).start()

    def store_result(self, request_id: str, result: Any) -> None:
        with self._result_lock:
            if len(self._result_store) >= self.MAX_RESULTS_CACHE:
                oldest_key = next(iter(self._result_store))
                del self._result_store[oldest_key]
            self._result_store[request_id] = result
            event = self._result_events.get(request_id)
            if event and not event.is_set():
                event.set()

    def get_result(self, request_id: str, remove: bool = True) -> Any:
        with self._result_lock:
            if request_id not in self._result_store:
                return None
            result = self._result_store[request_id]
            if remove:
                del self._result_store[request_id]
            return result

    def start(self) -> None:
        if self._running:
            return
        handler_class = cast(Any, HttpRequestHandler)
        self._httpd = ThreadingHTTPServer((self._host, self._port), handler_class)
        threading.Thread(target=self._httpd.serve_forever, daemon=True).start()
        self._running = True
        logging.info("PETP Background HTTP Server is serving at http://%s:%d", self._host or "localhost", self._port)

    def stop(self) -> None:
        if self._httpd and self._running:
            self._httpd.shutdown()
            self._running = False
            logging.info("PETP Background HTTP Server has been stopped")
