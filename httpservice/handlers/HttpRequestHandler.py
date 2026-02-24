import json
import logging
import re

from urllib.parse import parse_qs, urlparse
from http.server import SimpleHTTPRequestHandler
from collections.abc import Iterator
import types


class StreamingResponseData:
	"""Wrapper to carry streaming iterator plus headers/content type."""

	def __init__(self, iterator, headers=None, content_type=None, status_code=200):
		self.iterator = iterator
		self.headers = headers or {}
		self.content_type = content_type
		self.status_code = status_code


class HttpRequestHandler(SimpleHTTPRequestHandler):
	"""Enhanced HTTP request handler with routing capabilities"""
	protocol_version = "HTTP/1.1"

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
		path_for_routing = self.path  # Store original path for routing

		# Parse query parameters for all requests
		if '?' in self.path:
			url_parts = urlparse(self.path)
			query_params = parse_qs(url_parts.query)
			# Convert lists to single values for simple use
			params.update({k: v[0] if len(v) == 1 else v for k, v in query_params.items()})

			# Update path to remove query string for routing
			path_for_routing = url_parts.path
		else:
			path_for_routing = self.path

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

		return params, path_for_routing

	def find_handler(self, current_path):
		"""Find the appropriate handler for the current request with dynamic parameter support.

		Args:
			current_path: The path part of the URL, without query string.

		Returns:
			A tuple (handler_function, path_parameters_dict) or (None, {}).
		"""
		# Check for exact match first (most efficient)
		exact_route_key = f"{self.command}:{current_path}"
		if exact_route_key in self._routes:
			logging.debug(f"Exact route matched: {exact_route_key}")
			return self._routes[exact_route_key], {}

		# Then check for pattern matches
		for pattern_route_key, handler in self._routes.items():
			try:
				method, path_pattern = pattern_route_key.split(':', 1)
			except ValueError:
				logging.warning(f"Invalid route pattern format: {pattern_route_key}. Skipping.")
				continue

			if method != self.command:
				continue

			# Convert path_pattern with placeholders like {param_name} to a regex
			# 1. Escape any special regex characters in the path_pattern itself.
			regex_pattern_str = re.escape(path_pattern)

			# 2. Find all parameter names (e.g., 'id', 'name')
			param_names = re.findall(r'\\\{([^\\}]+)\\\}', regex_pattern_str)

			# 3. Replace the escaped placeholders (e.g., '\\{id\\}') with regex capture groups '([^/]+)'
			#    ([^/]+) matches one or more characters that are not a slash.
			for param_name in param_names:
				# Ensure we replace the fully escaped placeholder
				escaped_placeholder = re.escape(f"{{{param_name}}}")
				regex_pattern_str = regex_pattern_str.replace(escaped_placeholder, r'([^/]+)', 1)

			regex_pattern_str = f"^{regex_pattern_str}$"

			try:
				compiled_regex = re.compile(regex_pattern_str)
			except re.error as e:
				logging.error(f"Invalid regex generated from pattern '{path_pattern}': {regex_pattern_str}. Error: {e}")
				continue

			match = compiled_regex.match(current_path)

			if match:
				# Extract captured parameters
				path_params = {}
				captured_values = match.groups()
				if len(param_names) == len(captured_values):
					path_params = dict(zip(param_names, captured_values))
					logging.debug(
						f"Pattern route matched: {pattern_route_key} on path {current_path} with params: {path_params}")
					return handler, path_params
				else:
					logging.warning(
						f"Parameter name/value mismatch for route {pattern_route_key} and path {current_path}. "
						f"Expected {len(param_names)} params, got {len(captured_values)} values."
					)

		logging.debug(f"No handler found for {self.command}:{current_path}")
		return None, {}

	def send_cors_headers(self):
		"""Add CORS headers to response"""
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
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

	def do_DELETE(self):
		"""Handle DELETE requests"""
		self.process_request()

	def process_request(self):
		"""Process incoming requests with appropriate handler"""
		# Parse parameters and get the path for routing (without query string)
		params, path_for_routing = self.parse_request_params()
		if params is None:  # Parse error occurred in parse_request_params
			return

		# Find the handler for this route using the path_for_routing
		handler, path_params = self.find_handler(path_for_routing)

		if not handler:
			self.send_failure_response(404, msg="Endpoint not found")
			return

		# Merge path parameters into the main params dictionary.
		# Path parameters can override query/body parameters if names conflict.
		if path_params:
			params.update(path_params)

		try:
			# Execute handler
			result = handler(self, params)

			# Streamed responses (generators/iterators) -> chunked transfer
			if isinstance(result, StreamingResponseData):
				self.send_streaming_response(result.iterator, extra_headers=result.headers, content_type=result.content_type, status_code= result.status_code )
			elif self._is_streaming_result(result):
				self.send_streaming_response(result)
			# Handle tuple returns for custom status codes
			elif isinstance(result, tuple) and len(result) == 2:
				data, code = result
				self.send_success_json(code=code, data=data)
			else:
				self.send_success_json(data=result)

		except Exception as e:
			logging.exception(f"Error processing request: {str(e)}")
			self.send_failure_response(500, msg=f"Internal server error: {str(e)}")

	def _is_streaming_result(self, result):
		"""Determine if the handler returned a streaming iterator/generator."""
		if isinstance(result, (str, bytes, dict, list, tuple)):
			return False
		# GeneratorType covers plain generators; Iterator covers yield-based objects
		return isinstance(result, (types.GeneratorType, Iterator))

	def send_streaming_response(self, stream_iter, *, extra_headers=None, content_type=None, status_code):
		"""Send a chunked streaming response (text/plain by default)."""
		self.send_response(status_code)
		self.send_header('Content-Type', content_type or 'text/plain; charset=utf-8')
		self.send_header('Transfer-Encoding', 'chunked')
		if extra_headers:
			for k, v in extra_headers.items():
				self.send_header(k, v)
		self.send_cors_headers()
		self.end_headers()

		try:
			for chunk in stream_iter:
				if chunk is None:
					continue
				if isinstance(chunk, str):
					chunk_bytes = chunk.encode('utf-8')
				elif isinstance(chunk, bytes):
					chunk_bytes = chunk
				else:
					chunk_bytes = str(chunk).encode('utf-8')

				# Write chunk size in hex followed by CRLF, then data and CRLF
				size_line = f"{len(chunk_bytes):X}\r\n".encode('ascii')
				self.wfile.write(size_line)
				self.wfile.write(chunk_bytes)
				self.wfile.write(b"\r\n")
				self.wfile.flush()

			# Terminate chunked response
			self.wfile.write(b"0\r\n\r\n")
			self.wfile.flush()
		except Exception as e:
			logging.error(f"Error during streaming response: {e}")

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
