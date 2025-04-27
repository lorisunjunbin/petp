import json
import logging
import re
import threading
import time
import uuid
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import wx

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
		self.routes = {}
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
			'POST:/petp': self._handle_petp_event
		})

	def _generate_request_id(self):
		"""Generate a unique request ID for tracking async operations"""
		return str(uuid.uuid4())

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

	def get_and_remove_result(self, request_id, timeout=10):
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
					"description": "Trigger a PETP event - run test_read_from_excel",
					"uri": "/petp",
					"method": "POST",
					"payload": {
						"action": "execution",
						"params": {
							"execution": "test_read_from_excel",
							"fromHTTPService": "true"
						}
					}
				}
			]
		}

	def _handle_health(self, handler, params=None):
		"""Health check endpoint"""
		return {
			"status": "ok",
			"timestamp": time.time()
		}

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
		result = self.get_and_remove_result(request_id, timeout=self.http_request_timeout)

		if result is None:
			return {"error": "Request timed out"}, 408

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


class HttpRequestHandler(SimpleHTTPRequestHandler):
	"""Enhanced HTTP request handler with routing capabilities"""

	# Class variables for sharing across instances
	_view = None
	_routes = {}
	_server = None
	# Static global variable to store current request_id
	_request_id_key = '__http_request_id__'
	_response_key = '__http_response_key__'

	@classmethod
	def register_view(cls, view):
		"""Register the wxPython view for event dispatching"""
		cls._view = view

	@classmethod
	def get_view(cls):
		"""Get the registered view"""
		return cls._view

	@classmethod
	def register_server(cls, server):
		"""Register the server instance for result handling"""
		cls._server = server

	@classmethod
	def get_server(cls):
		"""Get the registered server"""
		return cls._server

	@classmethod
	def register_routes(cls, routes_dict):
		"""Register multiple route handlers at once

		Args:
			routes_dict: Dictionary of {METHOD:path: handler_function}
		"""
		cls._routes.update(routes_dict)

	@classmethod
	def get_request_id_key(cls):
		"""Get the HTTP request ID key"""
		return cls._request_id_key

	@classmethod
	def get_response_key(cls):
		"""Get the HTTP response key"""
		return cls._response_key

	def log_message(self, format, *args):
		"""Override to use Python's logging instead of stderr"""
		logging.info("%s - - [%s] %s" % (
			self.address_string(),
			self.log_date_time_string(),
			format % args
		))

	def parse_request_params(self):
		"""Parse parameters from request based on method and content type"""
		params = {}

		# Parse query parameters for all requests
		if '?' in self.path:
			url_parts = urlparse(self.path)
			query_params = parse_qs(url_parts.query)
			# Convert lists to single values for simple use
			params.update({k: v[0] if len(v) == 1 else v for k, v in query_params.items()})

			# Update path to remove query string for routing
			self.path = url_parts.path

		# Handle form data and JSON for POST, PUT
		if self.command in ['POST', 'PUT']:
			content_length = int(self.headers.get('Content-Length', 0))
			if content_length > 0:
				post_data = self.rfile.read(content_length)
				content_type = self.headers.get('Content-Type', '')

				if 'application/json' in content_type:
					try:
						json_params = json.loads(post_data.decode('utf-8'))
						params.update(json_params)
					except json.JSONDecodeError as e:
						logging.error(f"JSON decode error: {e}")
						self.send_error(400, message=f"Invalid JSON in request body: {str(e)}")
						return None

				elif 'application/x-www-form-urlencoded' in content_type:
					form_params = parse_qs(post_data.decode('utf-8'))
					params.update({k: v[0] if len(v) == 1 else v for k, v in form_params.items()})

		return params

	def find_handler(self):
		"""Find the appropriate handler for the current request"""
		route_key = f"{self.command}:{self.path}"

		# Check for exact match first
		if route_key in self._routes:
			return self._routes[route_key]

		# Then check for pattern matches
		for pattern, handler in self._routes.items():
			method, path_pattern = pattern.split(':', 1)
			if method != self.command:
				continue

			# Convert route patterns to regex patterns
			regex_pattern = "^" + path_pattern.replace("{id}", "([^/]+)") + "$"
			match = re.match(regex_pattern, self.path)

			if match:
				return handler

		return None

	def send_cors_headers(self):
		"""Add CORS headers to response"""
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
		self.send_header('Access-Control-Allow-Headers', 'Content-Type')

	def do_OPTIONS(self):
		"""Handle OPTIONS requests for CORS preflight"""
		self.send_response(200)
		self.send_cors_headers()
		self.end_headers()

	def do_GET(self):
		"""Handle GET requests"""
		self.process_request()

	def do_POST(self):
		"""Handle POST requests"""
		self.process_request()

	def process_request(self):
		"""Process incoming requests with appropriate handler"""
		# Find the handler for this route
		handler = self.find_handler()

		if not handler:
			self.send_failure_response(404, msg="Endpoint not found")
			return

		# Parse parameters
		params = self.parse_request_params()
		if params is None:  # Parse error occurred
			return

		try:
			# Execute handler
			result = handler(self, params)

			# Handle tuple returns for custom status codes
			if isinstance(result, tuple) and len(result) == 2:
				data, code = result
				self.send_success_json(code=code, data=data)
			else:
				self.send_success_json(data=result)

		except Exception as e:
			logging.exception(f"Error processing request: {str(e)}")
			self.send_failure_response(500, msg=f"Internal server error: {str(e)}")

	def send_failure_response(self, code=500, data={}, msg="Failure"):
		"""Send a failure JSON response with appropriate status code"""
		self.send_json_response(code, data, msg)

	def send_success_json(self, code=200, data={}, msg="Success"):
		"""Send a success JSON response with appropriate status code"""
		self.send_json_response(code, data, msg)

	def send_json_response(self, code=-1, data={}, msg=""):
		"""Send a JSON response with the given status code and data"""
		self.send_response(code)
		self.send_header('Content-Type', 'application/json')
		self.send_cors_headers()
		self.end_headers()
		self.wfile.write(json.dumps({
			"code": code,
			"data": data,
			"msg": msg
		}).encode('utf-8'))
