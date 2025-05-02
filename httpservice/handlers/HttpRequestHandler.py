import json
import logging
import re

from urllib.parse import parse_qs, urlparse
from http.server import SimpleHTTPRequestHandler

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
