import logging
import threading
import time
import uuid
from http.server import HTTPServer

import wx

from httpservice.handlers.HttpRequestHandler import HttpRequestHandler
from mvp.presenter import PETPPresenter
from mvp.presenter.event.PETPEvent import PETPEvent


class HttpServer:
	"""Enhanced HTTP Server for PETP with better routing and error handling"""

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

		# Result store for asynchronous event handling
		self._result_store = {}
		self._result_events = {}
		self._result_lock = threading.Lock()

		# Register the presenter's view
		HttpRequestHandler.register_view(p.v)

		# Register the server instance for result handling
		HttpRequestHandler.register_server(self)

		# Register default routes
		HttpRequestHandler.register_routes({
			'GET:/': self._handle_index,
			'GET:/health': self._handle_health,
			'GET:/petp/tools': self._handle_petp_tools,
			'POST:/petp/exec': self._handle_petp_event
		})

	def _handle_index(self, handler, params=None):
		"""Default handler for the index route"""
		return {
			"server": "PETP HTTP Server",
			"available_endpoints": [
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
				}
			]
		}

	def _handle_health(self, handler, params=None):
		"""Health check endpoint"""
		return {
			"status": "ok",
			"timestamp": time.time()
		}

	def _handle_petp_tools(self, handler, payload) -> dict:
		"""Handle PETP event requests"""
		return self.p.get_tools()

	def _handle_petp_event(self, handler, payload):
		"""Handle PETP event requests"""
		if not payload or 'action' not in payload or 'params' not in payload:
			return {"error": "Missing required 'action' or 'params' parameter"}, 400

		# Generate a unique request ID
		request_id = self._generate_request_id()

		# Add request ID to params
		payload['params'][HttpRequestHandler.get_request_id_key()] = request_id

		# Post event to the view (asynchronously)
		wx.PostEvent(HttpRequestHandler.get_view(), PETPEvent(PETPEvent.HTTP_REQUEST, payload))

		# Wait for the result with timeout
		result = self._get_and_remove_result(request_id, timeout=self.http_request_timeout)

		if result is None:
			return {"error": "Request timed out"}, 408

		return result

	def store_result(self, request_id, result):
		"""Store a result for an asynchronous operation

		Args:
			request_id: The unique ID of the request
			result: The result to store
		"""
		with self._result_lock:
			self._result_store[request_id] = result
			if request_id in self._result_events:
				self._result_events[request_id].set()
				
	def _generate_request_id(self):
		"""Generate a unique request ID for tracking async operations"""
		return str(uuid.uuid4())

	def _get_and_remove_result(self, request_id, timeout=10):
		"""Get and remove a result for the specified request ID
		
		Args:
			request_id: The unique ID of the request
			timeout: Maximum time to wait for the result in seconds
			
		Returns:
			The result or None if timed out
		"""
		if request_id not in self._result_events:
			self._result_events[request_id] = threading.Event()

		# Wait for the result
		result_ready = self._result_events[request_id].wait(timeout)

		with self._result_lock:
			if not result_ready:
				# Timed out
				if request_id in self._result_events:
					del self._result_events[request_id]
				return None

			result = self._result_store.get(request_id)

			# Clean up
			if request_id in self._result_store:
				del self._result_store[request_id]
			if request_id in self._result_events:
				del self._result_events[request_id]

			return result

	def start(self):
		"""Start the HTTP server in a daemon thread"""
		if self._running:
			logging.warning("HTTP Server is already running")
			return
		try:
			handler = HttpRequestHandler
			self.httpd = HTTPServer((self.host, self.port), handler)
			server_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
			server_thread.start()
			self._running = True
			logging.info(f"HTTP Server is serving at http://{self.host or 'localhost'}:{self.port}")
		except Exception as e:
			logging.error(f"Failed to start HTTP Server: {e}, so can not handle any http request by this instance.")
			self._running = False

	def stop(self):
		"""Stop the HTTP server if it's running"""
		if self.httpd and self._running:
			self.httpd.shutdown()
			self._running = False
			logging.info("HTTP Server has been stopped")
