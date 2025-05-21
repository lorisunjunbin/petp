import logging
import threading
import time
import uuid
from http.server import HTTPServer
import weakref
from collections import OrderedDict

import wx

from decorators.decorators import reload_http_log_after
from httpservice.handlers.HttpRequestHandler import HttpRequestHandler
from mvp.presenter import PETPPresenter
from mvp.presenter.event.PETPEvent import PETPEvent


class HttpServer:
	"""Enhanced HTTP Server for PETP with better routing and error handling"""

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
			'POST:/petp/exec': self._handle_petp_event
		})

	def _handle_index(self, handler, params=None):
		logging.debug(f"_handle_index params: {params}")
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
	def _handle_petp_event(self, handler, payload):

		logging.debug(f"_handle_petp_event payload: {payload}")

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
		"""Store a result for an asynchronous operation with safeguards

		Args:
			request_id: The unique ID of the request
			result: The result to store
		"""
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
		"""Get and remove a result with optimized resource management and error handling

		Args:
			request_id: The unique ID of the request
			timeout: Maximum time to wait for the result in seconds

		Returns:
			The result or None if timed out or error occurred
		"""
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
		"""Stop the HTTP server if it's running and perform cleanup"""
		# Stop the cleanup thread
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
