import json
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Any, Callable, Generator, Optional

from httpservice.constants import HTTP_RESPONSE_KEY
from httpservice.handlers.HttpRequestHandler import HttpRequestHandler, RawJsonResponse, StreamingResponseData


class McpMixin:
    """Shared MCP protocol helpers for HttpServer and BackgroundHttpServer."""

    _normalized_tools_cache_key: tuple | None = None
    _normalized_tools_cache_val: list[dict] = []

    # ------------------------------------------------------------------
    # SSE helpers
    # ------------------------------------------------------------------

    def _mcp_response(self, payload: dict, handler: HttpRequestHandler,
                       session_id: Optional[str] = None):
        accept = handler.headers.get("Accept", "") if handler else ""
        if "text/event-stream" in accept:
            return self._single_sse_response(payload, session_id)
        headers = {}
        if session_id:
            headers["mcp-session-id"] = session_id
        json_body = json.dumps(payload)
        return RawJsonResponse(json_body, headers, status_code=200)

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

    # ------------------------------------------------------------------
    # Tool normalization (PETP internal -> MCP tools/list schema)
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_tool_value(value: Any) -> dict:
        if isinstance(value, dict):
            return value
        if not isinstance(value, str) or not value.strip():
            return {}
        normalized = (
            value.replace("“", '"')
            .replace("”", '"')
            .replace("\n", "")
            .replace("：", ":")
        )
        try:
            return json.loads(normalized)
        except json.JSONDecodeError:
            logging.exception("Failed to parse tool value: %s", value)
            return {}

    @staticmethod
    def _compact_schema(schema: dict) -> dict:
        """Remove internal/redundant fields from a schema before sending to MCP client."""
        if not schema or "properties" not in schema:
            return schema
        cleaned = {k: v for k, v in schema.items() if k != "title"}
        cleaned["properties"] = {}
        for name, prop in schema.get("properties", {}).items():
            compact_prop = {}
            for k, v in prop.items():
                if k == "mapKey":
                    continue
                if k == "title" and v == name:
                    continue
                if k == "description" and (not v or not str(v).strip()):
                    continue
                compact_prop[k] = v
            cleaned["properties"][name] = compact_prop
        return cleaned

    @staticmethod
    def _build_input_schema(key: str, parsed: dict) -> Optional[dict]:
        if parsed.get("inputSchema"):
            return parsed["inputSchema"]
        params = parsed.get("params")
        if isinstance(params, list):
            clean_params = [p for p in params if isinstance(p, str) and p.strip()]
            return {
                "title": f"{key}Arguments",
                "type": "object",
                "properties": {p: {"title": p, "type": "string"} for p in clean_params},
                "required": clean_params,
            }
        return None

    @staticmethod
    def _build_output_schema(key: str, parsed: dict) -> Optional[dict]:
        if parsed.get("outputSchema"):
            return parsed["outputSchema"]
        out_params = parsed.get("outParams")
        if isinstance(out_params, list):
            clean_params = [p for p in out_params if isinstance(p, str) and p.strip()]
            if clean_params:
                return {
                    "title": f"{key}Output",
                    "type": "object",
                    "properties": {p: {"title": p, "type": "string"} for p in clean_params},
                    "required": clean_params,
                }
        return None

    def _normalize_tools(self, tools_petp: Any) -> list[dict]:
        if not isinstance(tools_petp, dict):
            return []
        cache_key = tuple(sorted(tools_petp.items()))
        if cache_key == self._normalized_tools_cache_key:
            return self._normalized_tools_cache_val
        result = []
        for key, value in tools_petp.items():
            parsed = self._parse_tool_value(value)
            tool: dict = {
                "name": key,
                "description": parsed.get("desc") or key,
            }
            input_schema = self._build_input_schema(key, parsed) or {
                "type": "object",
                "properties": {},
            }
            tool["inputSchema"] = self._compact_schema(input_schema)
            output_schema = self._build_output_schema(key, parsed)
            if output_schema:
                tool["outputSchema"] = self._compact_schema(output_schema)
            result.append(tool)
        self._normalized_tools_cache_key = cache_key
        self._normalized_tools_cache_val = result
        return result

    # ------------------------------------------------------------------
    # tools/call result helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_mcp_text(payload: Any) -> str:
        if isinstance(payload, str):
            return payload
        return json.dumps(payload, ensure_ascii=False, default=str)

    @staticmethod
    def _build_output_from_schema(data: dict, output_schema: dict) -> dict:
        properties = output_schema.get("properties", {})
        result = {}
        for prop_name, prop_spec in properties.items():
            dc_key = prop_spec.get("mapKey") or prop_name
            if '{' in dc_key and '}' in dc_key:
                try:
                    value = eval(f"f'{dc_key}'", {"__builtins__": {}}, data)
                except Exception:
                    continue
            elif dc_key in data:
                value = data[dc_key]
            else:
                continue
            declared_type = prop_spec.get("type")
            if declared_type == "string" and not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False, default=str)
            result[prop_name] = value
        return result

    @staticmethod
    def _strip_meta_for_client(result: Any) -> Any:
        if not isinstance(result, dict):
            return result
        return {k: v for k, v in result.items() if k != "meta"}

    @staticmethod
    def _is_mcp_error_result(result: Any) -> bool:
        if isinstance(result, dict):
            if "ok" in result:
                return not bool(result.get("ok"))
            if result.get("error"):
                return True
        return False

    @staticmethod
    def _extract_business_response(runtime_result: Any) -> Any:
        if not isinstance(runtime_result, dict):
            return runtime_result
        if not bool(runtime_result.get("ok")):
            return runtime_result
        data = runtime_result.get("data")
        if not isinstance(data, dict):
            return data
        response_key = data.get(HTTP_RESPONSE_KEY)
        if not isinstance(response_key, str) or not response_key:
            legacy_key = data.get("http_response_key")
            if isinstance(legacy_key, str) and legacy_key:
                response_key = legacy_key
        if isinstance(response_key, str) and response_key in data:
            return data.get(response_key)
        if "http_response" in data:
            return data.get("http_response")
        return data

    def _build_tools_call_result(self, tool_name: str, raw_result: Any, tools_getter) -> tuple[Any, Any]:
        """Return (client_result, structured_content) for a tools/call response.

        *tools_getter* is a zero-arg callable that returns the tools dict.
        """
        if self._is_mcp_error_result(raw_result):
            error_msg = ""
            if isinstance(raw_result, dict):
                error_msg = raw_result.get("error") or ""
            structured_content = {"error": error_msg} if error_msg else {"error": "execution failed"}
            return structured_content, structured_content

        raw = tools_getter().get(tool_name)
        output_schema = None
        if raw:
            parsed = self._parse_tool_value(raw)
            schema = parsed.get("outputSchema")
            if isinstance(schema, dict) and schema.get("properties"):
                output_schema = schema

        if output_schema and isinstance(raw_result, dict) and raw_result.get("ok"):
            data = raw_result.get("data", {}) if isinstance(raw_result.get("data"), dict) else {}
            client_result = self._build_output_from_schema(data, output_schema)
        else:
            extracted = self._extract_business_response(raw_result)
            client_result = self._strip_meta_for_client(extracted)

        structured_content = client_result if isinstance(client_result, dict) else {"result": client_result}
        return client_result, structured_content

    def _mcp_tools_call_json_response(self, request_id: Any, session_id: Optional[str],
                                       raw_result: Any, tool_name: str,
                                       tools_getter: Callable, handler: 'HttpRequestHandler') -> StreamingResponseData:
        client_result, structured_content = self._build_tools_call_result(
            tool_name, raw_result, tools_getter
        )
        is_error = self._is_mcp_error_result(raw_result)
        if is_error:
            error_msg = structured_content.get("error", "unknown error") if isinstance(structured_content, dict) else "unknown error"
            content_text = f"[{tool_name}] error: {error_msg}"
        else:
            content_text = f"[{tool_name}] ok"
        if isinstance(raw_result, dict) and raw_result.get("meta") is not None:
            logging.info("MCP tools/call meta for %s: %s", tool_name,
                         json.dumps(raw_result.get("meta"), ensure_ascii=False, default=str))
        resp = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": content_text}],
                "structuredContent": structured_content,
                "isError": is_error,
            },
        }
        return self._mcp_response(resp, handler, session_id)

    @staticmethod
    def _wants_sse(handler: 'HttpRequestHandler') -> bool:
        accept = handler.headers.get("Accept", "") if handler else ""
        return "text/event-stream" in accept

    def _run_with_timeout(self, fn: Callable[[], Any], timeout: int) -> Any:
        with ThreadPoolExecutor(1) as pool:
            future = pool.submit(fn)
            try:
                return future.result(timeout=timeout)
            except FuturesTimeoutError:
                return {"ok": False, "error": f"Tool execution timed out after {timeout}s"}

    _PROGRESS_INTERVAL: int = 1
    _FAST_CHECK_TIMEOUT: float = 0.05

    def _run_with_progress(self, fn: Callable[[], Any], timeout: int,
                            tool_name: str) -> Generator[Any, None, None]:
        with ThreadPoolExecutor(1) as pool:
            future = pool.submit(fn)
            try:
                result = future.result(timeout=self._FAST_CHECK_TIMEOUT)
                yield result
                return
            except FuturesTimeoutError:
                pass
            elapsed = 0
            while not future.done():
                try:
                    result = future.result(timeout=self._PROGRESS_INTERVAL)
                    yield result
                    return
                except FuturesTimeoutError:
                    elapsed += self._PROGRESS_INTERVAL
                    if elapsed >= timeout:
                        yield {"ok": False, "error": f"Tool execution timed out after {timeout}s"}
                        return
                    yield self._sse_event({
                        "jsonrpc": "2.0",
                        "method": "notifications/message",
                        "params": {"level": "info", "data": f"[{tool_name}] still running... ({elapsed}s)"},
                    })
            yield future.result()

    # ------------------------------------------------------------------
    # Batch request support
    # ------------------------------------------------------------------

    def _handle_mcp_batch(self, handler: 'HttpRequestHandler', batch: list,
                           single_handler: Callable) -> StreamingResponseData:
        session_id = self._extract_session_id(handler)
        responses: list[dict] = []
        for item in batch:
            if not isinstance(item, dict):
                responses.append({
                    "jsonrpc": "2.0", "id": None,
                    "error": {"code": -32600, "message": "Invalid Request"},
                })
                continue
            result = single_handler(handler, item)
            if isinstance(result, StreamingResponseData):
                for chunk in result.iterator:
                    if chunk.startswith("event: message\ndata: "):
                        data_str = chunk.split("data: ", 1)[1].rstrip("\n")
                        try:
                            parsed = json.loads(data_str)
                            if "id" in parsed:
                                responses.append(parsed)
                        except json.JSONDecodeError:
                            pass
            elif isinstance(result, dict):
                responses.append(result)

        resp_payload = responses if len(responses) > 1 else (responses[0] if responses else {})
        return self._single_sse_response(resp_payload, session_id)

    # ------------------------------------------------------------------
    # MCP protocol frames
    # ------------------------------------------------------------------

    def _mcp_initialize_response(self, request_id: Any, protocol_version: str, session_id: str,
                                  server_name: str, handler: Optional[HttpRequestHandler] = None) -> StreamingResponseData:
        resp = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": protocol_version,
                "capabilities": {
                    "tools": {"listChanged": False},
                },
                "serverInfo": {"name": server_name, "version": "1.0.0"},
            },
        }
        return self._mcp_response(resp, handler, session_id)

    def _mcp_initialized_response(self, session_id: Optional[str]) -> StreamingResponseData:
        headers = {}
        if session_id:
            headers["mcp-session-id"] = session_id
        return StreamingResponseData(
            iter([]),
            headers,
            content_type="text/plain",
            status_code=202,
        )

    def _mcp_tools_list_response(self, request_id: Any, session_id: Optional[str],
                                  tools_petp: Any, handler: Optional[HttpRequestHandler] = None) -> StreamingResponseData:
        tools_payload = self._normalize_tools(tools_petp)
        resp = {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools_payload}}
        logging.info("PETP MCP Tools: %s", json.dumps(resp))
        return self._mcp_response(resp, handler, session_id)

    def _mcp_method_not_found(self, request_id: Any, method: str,
                               session_id: Optional[str], handler: Optional[HttpRequestHandler] = None) -> StreamingResponseData:
        resp = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
        return self._mcp_response(resp, handler, session_id)

    @staticmethod
    def _generate_request_id() -> str:
        return str(uuid.uuid4())
