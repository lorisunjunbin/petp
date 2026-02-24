# client.py
from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession
import logging
import utils.Logger as Logger

import asyncio
import mcp.types as types
from mcp.shared.session import RequestResponder

Logger.init('mcp_client_4_petp')


class LoggingCollector:
    def __init__(self):
        self.log_messages: list[types.LoggingMessageNotificationParams] = []

    async def __call__(self, params: types.LoggingMessageNotificationParams) -> None:
        self.log_messages.append(params)
        logging.info("MCP Log: %s - %s", params.level, params.data)


logging_collector = LoggingCollector()
port = 8866


async def message_handler(
        message: RequestResponder[types.ServerRequest, types.ClientResult]
                 | types.ServerNotification
                 | Exception,
) -> None:
    logging.info("Received message: %s", message)
    if isinstance(message, Exception):
        logging.error("Exception received!")
        raise message
    elif isinstance(message, types.ServerNotification):
        logging.info("NOTIFICATION: %s", message)
    elif isinstance(message, RequestResponder):
        logging.info("REQUEST_RESPONDER: %s", message)
    else:
        logging.info("SERVER_MESSAGE: %s", message)


async def main():
    logging.info("Starting client...")
    # call method process_files
    async with streamable_http_client(f"http://localhost:{port}/mcp") as (
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
            id_before = session_callback()
            logging.info("Session ID before init: %s", id_before)
            await session.initialize()
            id_after = session_callback()
            logging.info("Session ID after init: %s", id_after)
            logging.info("Session initialized, ready to call tools.")

            list_tool_result = await session.list_tools()
            logging.info("List tool result: %s", list_tool_result)

            tool_result: types.CallToolResult = await session.call_tool("ENDECODER",
                                                                        {"type": "encode", "algorithms": "Base64",
                                                                         "inbound": "Hello, PETP!"})
            logging.info("Tool result ENDECODER: %s", tool_result.structuredContent)

            tool_result = await session.call_tool("ENDECODER",
                                                  {"type": "decode", "algorithms": "Base64",
                                                   "inbound": tool_result.structuredContent.get('text')})
            logging.info("Tool result ENDECODER: %s", tool_result.structuredContent)

            tool_result = await session.call_tool("OOTB_BS4_GET_DATA_FROM_news.ceic.ac.cn", {})
            logging.info("Tool result OOTB_BS4_GET_DATA_FROM_news.ceic.ac.cn: %s", tool_result.structuredContent)

            if logging_collector.log_messages:
                logging.info("Collected log messages:")
                for log in logging_collector.log_messages:
                    logging.info("Log: %s", log)

            session.complete()


if __name__ == "__main__":
    logging.info("Running MCP client...")
    asyncio.run(main())
