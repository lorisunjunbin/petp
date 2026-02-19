# client.py
import logging

import mcp.types as types
import requests

# Configure logging
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('mcp_client')


class LoggingCollector:
	def __init__(self):
		self.log_messages: list[types.LoggingMessageNotificationParams] = []

	async def __call__(self, params: types.LoggingMessageNotificationParams) -> None:
		self.log_messages.append(params)
		logger.info("MCP Log: %s - %s", params.level, params.data)


logging_collector = LoggingCollector()
# port = 8001
port = 8866


def stream_progress(message="hello", url=f"http://localhost:{port}/stream"):
	params = {"message": message}
	logger.info("Connecting to %s with message: %s", url, message)
	try:
		with requests.get(url, params=params, stream=True, timeout=10) as r:
			r.raise_for_status()
			logger.info("--- Streaming Progress ---")
			for line in r.iter_lines():
				if line:
					# Still print the streamed content to stdout for visibility
					decoded_line = line.decode().strip()
					print(decoded_line)
					logger.debug("Stream content: %s", decoded_line)
			logger.info("--- Stream Ended ---")
	except requests.RequestException as e:
		logger.error("Error during streaming: %s", e)


if __name__ == "__main__":
	# Classic HTTP streaming client mode
	logger.info("Running classic HTTP streaming client...")
	stream_progress()
