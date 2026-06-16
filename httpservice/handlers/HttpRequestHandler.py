import json
import logging
import os
import re

from urllib.parse import parse_qs, urlparse
from http.server import SimpleHTTPRequestHandler
from collections.abc import Iterator
import types

from httpservice.constants import HTTP_REQUEST_ID_KEY, HTTP_RESPONSE_KEY


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name, '').strip()
    if not raw:
        return default
    try:
        v = int(raw)
        return v if v > 0 else default
    except ValueError:
        return default


# Phase 2 P1-3: cap request body and batch array sizes to avoid trivial DoS.
# Both are env-tunable for ops; defaults err toward safe-by-default for the
# Tailscale Funnel deployment scenario where /mcp is publicly reachable.
MAX_BODY_BYTES = _int_env('PETP_MAX_BODY_BYTES', 4 * 1024 * 1024)   # 4 MiB
MAX_BATCH_ITEMS = _int_env('PETP_MAX_BATCH_ITEMS', 64)


class StreamingResponseData:
    """Wrapper to carry streaming iterator plus headers/content type.

    Optional ``cancel_event`` is a ``threading.Event`` that the handler will
    ``set()`` when the peer disconnects mid-stream, allowing the producing
    generator to short-circuit instead of running to completion.
    """

    def __init__(self, iterator, headers=None, content_type=None, status_code=200, cancel_event=None):
        self.iterator = iterator
        self.headers = headers or {}
        self.content_type = content_type
        self.status_code = status_code
        self.cancel_event = cancel_event


class RawJsonResponse:
    """Non-chunked JSON response with custom headers (no wrapper envelope)."""

    def __init__(self, body: str, headers=None, status_code=200):
        self.body = body
        self.headers = headers or {}
        self.status_code = status_code


class HttpRequestHandler(SimpleHTTPRequestHandler):
    """Enhanced HTTP request handler with routing capabilities"""
    protocol_version = "HTTP/1.1"

    # Class variables for sharing across instances
    _view = None
    _routes = {}
    _server = None
    # Static global variable to store current request_id
    _request_id_key = HTTP_REQUEST_ID_KEY
    _response_key = HTTP_RESPONSE_KEY

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

    # Errors that mean the remote peer simply closed the connection.
    # We treat them as debug-level noise, not server errors.
    _PEER_DISCONNECT_ERRORS = (
        ConnectionResetError,   # [Errno 54] on macOS / [Errno 104] on Linux
        BrokenPipeError,        # write to a closed socket
        ConnectionAbortedError, # Windows peer-abort equivalent
    )

    def handle(self):
        """Override to silently absorb peer-disconnect errors.

        Python's socketserver prints a full traceback to stderr for *any*
        unhandled exception in process_request_thread.  Catching the
        connection-reset family here prevents those noisy tracebacks while
        still letting genuine errors propagate.
        """
        try:
            super().handle()
        except self._PEER_DISCONNECT_ERRORS as e:
            logging.info(
                "Client %s disconnected before the request was fully read: %s",
                self.client_address,
                e,
            )

    def log_message(self, format, *args):
        logging.debug("%s - - [%s] %s" % (
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
            if content_length > MAX_BODY_BYTES:
                logging.warning(
                    "Rejecting %s %s: Content-Length %d exceeds MAX_BODY_BYTES %d",
                    self.command, self.path, content_length, MAX_BODY_BYTES
                )
                self.send_error(413, message=f"Request body too large (limit: {MAX_BODY_BYTES} bytes)")
                return None
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                content_type = self.headers.get('Content-Type', '')

                if 'application/json' in content_type:
                    try:
                        json_params = json.loads(post_data.decode('utf-8'))
                        if isinstance(json_params, list):
                            if len(json_params) > MAX_BATCH_ITEMS:
                                logging.warning(
                                    "Rejecting batch with %d items > MAX_BATCH_ITEMS %d",
                                    len(json_params), MAX_BATCH_ITEMS
                                )
                                self.send_error(
                                    400,
                                    message=f"Batch array too large (limit: {MAX_BATCH_ITEMS} items)"
                                )
                                return None
                            params['_batch'] = json_params
                        else:
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

        # Optional metrics hook — BG server attaches `_metrics`; GUI server doesn't
        metrics = getattr(self._server, "_metrics", None) if self._server else None
        endpoint_key = f"{self.command}:{path_for_routing}"
        token = metrics.record_start(endpoint_key) if metrics is not None else None
        record_end_handled_by_streaming = False
        status_code: int = 200
        exception_flag = False

        try:
            # Execute handler
            result = handler(self, params)
            status_code = self._extract_status_code(result)

            # Raw JSON response (MCP JSON path) -> Content-Length, no chunked
            if isinstance(result, RawJsonResponse):
                self.send_raw_json_response(result)
            # Streamed responses (generators/iterators) -> chunked transfer
            elif isinstance(result, StreamingResponseData):
                record_end_handled_by_streaming = True
                self.send_streaming_response(result.iterator, extra_headers=result.headers,
                                             content_type=result.content_type, status_code=result.status_code,
                                             cancel_event=result.cancel_event,
                                             metrics_token=token, metrics=metrics)
            elif self._is_streaming_result(result):
                record_end_handled_by_streaming = True
                self.send_streaming_response(result, metrics_token=token, metrics=metrics)
            # Handle tuple returns for custom status codes
            elif isinstance(result, tuple) and len(result) == 2:
                data, code = result
                self.send_success_json(code=code, data=data)
            else:
                self.send_success_json(data=result)

        except Exception as e:
            exception_flag = True
            status_code = 500
            logging.exception(f"Error processing request: {str(e)}")
            self.send_failure_response(500, msg=f"Internal server error: {str(e)}")
        finally:
            if token is not None and not record_end_handled_by_streaming:
                try:
                    metrics.record_end(token, status_code, exception=exception_flag)
                except Exception:
                    logging.exception("metrics.record_end failed")

    @staticmethod
    def _extract_status_code(result) -> int:
        """Best-effort HTTP status code extraction from a handler return value."""
        if isinstance(result, tuple) and len(result) == 2:
            try:
                return int(result[1])
            except (TypeError, ValueError):
                return 200
        if isinstance(result, RawJsonResponse):
            return getattr(result, "status_code", 200)
        if isinstance(result, StreamingResponseData):
            return getattr(result, "status_code", 200)
        return 200

    def _is_streaming_result(self, result):
        """Determine if the handler returned a streaming iterator/generator."""
        if isinstance(result, (str, bytes, dict, list, tuple)):
            return False
        # GeneratorType covers plain generators; Iterator covers yield-based objects
        return isinstance(result, (types.GeneratorType, Iterator))

    def send_streaming_response(self, stream_iter, *, extra_headers=None, content_type=None, status_code,
                                cancel_event=None, metrics_token=None, metrics=None):
        """Send a chunked streaming response (text/plain by default)."""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type or 'text/plain; charset=utf-8')
        self.send_header('Transfer-Encoding', 'chunked')
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.send_cors_headers()
        self.end_headers()

        exception_flag = False
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
        except self._PEER_DISCONNECT_ERRORS as e:
            # Client closed the connection mid-stream — not a server error.
            logging.debug("Client %s disconnected during streaming: %s", self.client_address, e)
            if cancel_event is not None:
                cancel_event.set()
        except Exception as e:
            exception_flag = True
            logging.error(f"Error during streaming response: {e}")
        finally:
            if metrics_token is not None and metrics is not None:
                try:
                    metrics.record_end(metrics_token, status_code, exception=exception_flag)
                except Exception:
                    logging.exception("metrics.record_end failed (streaming)")

    def send_raw_json_response(self, response: 'RawJsonResponse'):
        """Send a raw JSON response with Content-Length (no envelope wrapper)."""
        body_bytes = response.body.encode('utf-8')
        self.send_response(response.status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body_bytes)))
        for k, v in response.headers.items():
            self.send_header(k, v)
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body_bytes)
        self.wfile.flush()

    def send_failure_response(self, code=500, data=None, msg="Failure"):
        """Send a failure JSON response with appropriate status code"""
        self.send_json_response(code, data, msg)

    def send_success_json(self, code=200, data=None, msg="Success"):
        """Send a success JSON response with appropriate status code"""
        self.send_json_response(code, data, msg)

    def send_json_response(self, code=-1, data=None, msg=""):
        """Send a JSON response with the given status code and data"""
        if data is None:
            data = {}
        response_body: bytes = json.dumps({
            "code": code,
            "data": data,
            "msg": msg
        }).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(response_body)
