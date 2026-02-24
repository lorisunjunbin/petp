# client.py
import asyncio
import logging

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.session import RequestResponder
import mcp.types as types
import utils.Logger as Logger

Logger.init('mcp_client_4_petp')

# Constant configuration
PORT = 8866
BASE_URL = f"http://localhost:{PORT}/mcp"

# Tool names / payloads
ENDECODER_TOOL = "ENDECODER"
CEIC_TOOL = "OOTB_BS4_GET_DATA_FROM_news.ceic.ac.cn"


class LoggingCollector:
    """Collects logging notifications from MCP and mirrors them to app logs."""
    def __init__(self) -> None:
        self.log_messages: list[types.LoggingMessageNotificationParams] = []

    async def __call__(self, params: types.LoggingMessageNotificationParams) -> None:
        self.log_messages.append(params)
        logging.info("MCP Log: %s - %s", params.level, params.data)


logging_collector = LoggingCollector()


async def message_handler(
    message: RequestResponder[types.ServerRequest, types.ClientResult]
    | types.ServerNotification
    | Exception,
) -> None:
    """Handle all messages emitted by the MCP session."""
    logging.info("Received message: %s", message)
    if isinstance(message, Exception):
        logging.error("Exception received!")
        raise message
    if isinstance(message, types.ServerNotification):
        logging.info("NOTIFICATION: %s", message)
        return
    if isinstance(message, RequestResponder):
        logging.info("REQUEST_RESPONDER: %s", message)
        return
    logging.info("SERVER_MESSAGE: %s", message)


async def main() -> None:
    """Entry point for the MCP client workflow."""
    logging.info("Starting client...")

    # Open a streamable HTTP session to MCP
    async with streamable_http_client(BASE_URL) as (
        read_stream,
        write_stream,
        session_callback,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
            logging_callback=logging_collector,
            message_handler=message_handler,
        ) as session:
            # Session lifecycle
            logging.info("Session ID before init: %s", session_callback())
            await session.initialize()
            logging.info("Session ID after init: %s", session_callback())
            logging.info("Session initialized, ready to call tools.")

            # List available tools
            list_tool_result = await session.list_tools()
            logging.info("List tool result: %s", list_tool_result)

            # Encode text
            tool_result: types.CallToolResult = await session.call_tool(
                ENDECODER_TOOL,
                {"type": "encode", "algorithms": "Base64", "inbound": "Hello, PETP!"},
            )
            logging.info("Tool result ENDECODER: %s", tool_result.structuredContent)

            # Decode text using previous output
            tool_result = await session.call_tool(
                ENDECODER_TOOL,
                {
                    "type": "decode",
                    "algorithms": "Base64",
                    "inbound": tool_result.structuredContent.get("text"),
                },
            )
            logging.info("Tool result ENDECODER: %s", tool_result.structuredContent)

            # Fetch CEIC data
            tool_result = await session.call_tool(CEIC_TOOL, {})
            logging.info("Tool result %s: %s", CEIC_TOOL, tool_result.structuredContent)

            # Dump collected logs (if any)
            if logging_collector.log_messages:
                logging.info("Collected log messages:")
                for log in logging_collector.log_messages:
                    logging.info("Log: %s", log)

            await session.complete()


if __name__ == "__main__":
    logging.info("Running MCP client...")
    asyncio.run(main())
