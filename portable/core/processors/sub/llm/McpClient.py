import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import mcp.types as types


@dataclass
class McpTool:
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class McpToolResult:
    content_text: str = ''
    structured_content: Optional[Dict[str, Any]] = None
    is_error: bool = False


class McpClient:
    """Synchronous MCP client wrapper for use in threaded PETP processors."""

    def __init__(self, server_url: str, headers: Optional[Dict[str, str]] = None,
                 timeout_seconds: float = 30.0):
        self._server_url = server_url
        self._headers = headers or {}
        self._timeout_seconds = timeout_seconds

    def list_tools(self) -> List[McpTool]:
        return self._run_async(self._async_list_tools())

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> McpToolResult:
        return self._run_async(self._async_call_tool(name, arguments))

    def _run_async(self, coro):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        with ThreadPoolExecutor(1) as pool:
            return pool.submit(asyncio.run, coro).result(timeout=self._timeout_seconds)

    def _create_http_client(self) -> Optional[httpx.AsyncClient]:
        if not self._headers:
            return None
        return httpx.AsyncClient(headers=self._headers)

    async def _async_list_tools(self) -> List[McpTool]:
        http_client = self._create_http_client()
        try:
            async with streamable_http_client(
                self._server_url, http_client=http_client
            ) as (read_stream, write_stream, _get_session_id):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result: types.ListToolsResult = await session.list_tools()
                    return [
                        McpTool(
                            name=tool.name,
                            description=tool.description or tool.name,
                            input_schema=tool.inputSchema,
                        )
                        for tool in result.tools
                    ]
        finally:
            if http_client:
                await http_client.aclose()

    async def _async_call_tool(self, name: str, arguments: Dict[str, Any]) -> McpToolResult:
        http_client = self._create_http_client()
        try:
            async with streamable_http_client(
                self._server_url, http_client=http_client
            ) as (read_stream, write_stream, _get_session_id):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result: types.CallToolResult = await session.call_tool(name, arguments)

                    text_parts = []
                    for block in (result.content or []):
                        if hasattr(block, 'text'):
                            text_parts.append(block.text)

                    return McpToolResult(
                        content_text='\n'.join(text_parts),
                        structured_content=result.structuredContent,
                        is_error=bool(result.isError),
                    )
        finally:
            if http_client:
                await http_client.aclose()
