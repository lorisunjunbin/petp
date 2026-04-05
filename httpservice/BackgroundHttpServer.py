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
from httpservice.handlers.HttpRequestHandler import HttpRequestHandler, StreamingResponseData


class BackgroundHttpServer:
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
            "GET:/mcp": self._handle_mcp,
            "POST:/mcp": self._handle_mcp,
            "DELETE:/mcp": self._handle_mcp,
            "GET:/mcp/.well-known/openid-configuration": self._handle_mcp_auth,
        }

    def _handle_index(self, handler: HttpRequestHandler, params: Optional[dict] = None) -> dict:
        return {
            "server": "PETP Background HTTP Server",
            "available_endpoints": ["/health", "/petp/exec", "/petp/tools", "/petp/result", "/mcp"],
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

    def _handle_mcp_auth(self, handler: HttpRequestHandler, params: Optional[dict] = None) -> tuple:
        return {"token": self._token}, 200

    def _handle_mcp(
            self,
            handler: HttpRequestHandler,
            params: Optional[dict] = None,
    ) -> Union[StreamingResponseData, tuple]:
        params = params or {}
        token = handler.headers.get("Authorization")
        if self._token and token != f"Bearer {self._token}":
            return {"error": "Invalid token"}, 403

        session_id = self._extract_session_id(handler)

        method = params.get("method")
        if not method:
            return self._single_sse_response({"jsonrpc": "2.0", "id": None, "result": {"name": "PETP MCP"}}, session_id)

        if method == "initialize":
            session_id = session_id or (uuid.uuid4().hex + uuid.uuid4().hex)
            response = {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "result": {
                    "protocolVersion": handler.headers.get("mcp-protocol-version") or "2025-11-25",
                    "capabilities": {
                        "experimental": {},
                        "prompts": {"listChanged": False},
                        "resources": {"subscribe": False, "listChanged": False},
                        "tools": {"listChanged": False},
                    },
                    "serverInfo": {"name": "PETP Background MCP", "version": "1.0.0"},
                },
            }
            return self._single_sse_response(response, session_id)

        if method == "notifications/initialized":
            return StreamingResponseData(
                self._single_sse_chunk({}),
                self._build_sse_headers(session_id),
                "text/event-stream",
                202,
            )

        if method == "tools/list":
            tools = self._normalize_tools(self.runtime.get_tools())
            response = {"jsonrpc": "2.0", "id": params.get("id"), "result": {"tools": tools}}
            return self._single_sse_response(response, session_id)

        if method == "prompts/list":
            response = {"jsonrpc": "2.0", "id": params.get("id"), "result": {"prompts": []}}
            return self._single_sse_response(response, session_id)

        if method == "resources/list":
            response = {"jsonrpc": "2.0", "id": params.get("id"), "result": {"resources": []}}
            return self._single_sse_response(response, session_id)

        if method == "tools/call":
            request_id = params.get("id")
            tool_name = params.get("params", {}).get("name")
            arguments = params.get("params", {}).get("arguments", {})
            if not isinstance(tool_name, str) or not tool_name:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32602, "message": "Invalid params: params.name is required"},
                }
                return self._single_sse_response(response, session_id)
            tool_exec_name: str = cast(str, tool_name)

            arguments_json = json.dumps(arguments, ensure_ascii=False)

            def _stream_call_result() -> Generator[str, None, None]:
                info = f"call tool: {tool_name} with params: {arguments_json}"
                yield self._sse_event({
                    "jsonrpc": "2.0",
                    "method": "notifications/message",
                    "params": {"level": "info", "data": info},
                })

                result = self.runtime.run_execution(tool_exec_name, arguments)
                extracted_result = self._extract_business_response(result)
                client_result = self._strip_meta_for_client(extracted_result)
                content_text = self._to_mcp_text(client_result)
                if isinstance(result, dict) and result.get("meta") is not None:
                    logging.info("MCP tools/call meta for %s: %s", tool_name,
                                 json.dumps(result.get("meta"), ensure_ascii=False, default=str))
                yield self._sse_event({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": f" {info} -> {content_text}"}],
                        "structuredContent": self._to_mcp_structured_content(client_result),
                        "isError": not bool(result.get("ok", False)) if isinstance(result, dict) else True,
                    },
                })

            return StreamingResponseData(_stream_call_result(), self._build_sse_headers(session_id),
                                         "text/event-stream", 200)

        response = {
            "jsonrpc": "2.0",
            "id": params.get("id"),
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
        return self._single_sse_response(response, session_id)

    def _single_sse_response(self, payload: dict, session_id: Optional[str] = None) -> StreamingResponseData:
        return StreamingResponseData(
            self._single_sse_chunk(payload),
            self._build_sse_headers(session_id),
            content_type="text/event-stream",
            status_code=200,
        )

    def _single_sse_chunk(self, payload: dict) -> Generator[str, None, None]:
        yield self._sse_event(payload)

    @staticmethod
    def _sse_event(payload: dict) -> str:
        return f"event: message\ndata: {json.dumps(payload)}\n\n"

    @staticmethod
    def _build_sse_headers(session_id: Optional[str] = None) -> dict[str, str]:
        headers = {
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "Transfer-Encoding": "chunked",
            "X-Accel-Buffering": "no",
        }
        if session_id:
            headers["mcp-session-id"] = session_id
        return headers

    @staticmethod
    def _extract_session_id(handler: HttpRequestHandler) -> Optional[str]:
        return (
                handler.headers.get("mcp-session-id")
                or handler.headers.get("MCP-Session-Id")
                or handler.headers.get("Mcp-Session-Id")
        )

    @staticmethod
    def _normalize_tools(tools_petp: Any) -> list[dict]:
        if not isinstance(tools_petp, dict):
            return []

        tools = []
        for name, raw_value in tools_petp.items():
            parsed = BackgroundHttpServer._parse_tool_value(raw_value)
            raw_params = parsed.get("params") if isinstance(parsed.get("params"), list) else []
            params_list = cast(list[Any], raw_params)
            clean_params = [p for p in params_list if isinstance(p, str) and p.strip()]
            tools.append(
                {
                    "name": name,
                    "description": parsed.get("desc") or name,
                    "inputSchema": {
                        "type": "object",
                        "properties": {k: {"type": "string", "title": k} for k in clean_params},
                        "required": clean_params,
                    },
                }
            )
        return tools

    @staticmethod
    def _to_mcp_text(payload: Any) -> str:
        if isinstance(payload, str):
            return payload
        return json.dumps(payload, ensure_ascii=False, default=str)

    @staticmethod
    def _to_mcp_structured_content(payload: Any) -> dict[str, Any]:
        return {
            "type": "text",
            "text": payload,
            "annotations": None,
            "_meta": None,
        }

    @staticmethod
    def _strip_meta_for_client(result: Any) -> Any:
        if not isinstance(result, dict):
            return result
        return {k: v for k, v in result.items() if k != "meta"}

    @staticmethod
    def _extract_business_response(runtime_result: Any) -> Any:
        if not isinstance(runtime_result, dict):
            return runtime_result

        if not bool(runtime_result.get("ok")):
            return runtime_result

        data = runtime_result.get("data")
        if not isinstance(data, dict):
            return data

        response_key = data.get("__http_response_key__")
        if not isinstance(response_key, str) or not response_key:
            legacy_key = data.get("http_response_key")
            if isinstance(legacy_key, str) and legacy_key:
                response_key = legacy_key

        if isinstance(response_key, str) and response_key in data:
            return data.get(response_key)

        if "http_response" in data:
            return data.get("http_response")

        return data

    @staticmethod
    def _status_code_for_result(result: Any) -> int:
        if isinstance(result, dict) and "ok" in result:
            return 200 if bool(result.get("ok")) else 500
        return 200

    @staticmethod
    def _parse_tool_value(value: Any) -> dict:
        if isinstance(value, dict):
            return value
        if not isinstance(value, str) or not value.strip():
            return {}

        normalized = (
            value.replace("\u201c", '"')
            .replace("\u201d", '"')
            .replace("\n", "")
            .replace("\uff1a", ":")
        )
        try:
            return json.loads(normalized)
        except Exception:
            logging.exception("Failed to parse mcp_desc: %s", value)
            return {}

    def _submit_async(self, request_id: str, task: Callable[[], dict]) -> None:
        event = threading.Event()
        with self._result_lock:
            self._result_events[request_id] = event

        def _runner():
            runtime_result = task()
            client_result = self._extract_business_response(runtime_result)
            self.store_result(request_id, client_result)

        threading.Thread(target=_runner, daemon=True).start()

    @staticmethod
    def _generate_request_id() -> str:
        return str(uuid.uuid4())

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
        logging.info("Background HTTP Server is serving at http://%s:%d", self._host or "localhost", self._port)

    def stop(self) -> None:
        if self._httpd and self._running:
            self._httpd.shutdown()
            self._running = False
            logging.info("Background HTTP Server has been stopped")
