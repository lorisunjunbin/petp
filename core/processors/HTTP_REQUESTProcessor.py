import base64
import hashlib
import io
import json
import logging
import time
import zipfile

import requests

from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil


class HTTP_REQUESTProcessor(Processor):
    TPL: str = '{"timeout":60, "session_key":"__session_key","resp_fn":"return response.text if response.status_code == 200 else response.status_code", "request_url":"", "headers":"header1[>value1|header2[>value2", "method":"get|post", "params":"pk1[>pv1|pk2[>pv2","data_raw":"","data":"dk1[>dv1|dk2[>dv2", "data_key":"", "value_key":"", "verify":"yes|no", "is_zip_response":"yes|no", "filter_fn":"return True", "convert_fn":"return file_content.decode(\'utf-8\')", "basic_auth_user":"", "basic_auth_pwd":"", "oauth_token_url":"", "oauth_client_id":"", "oauth_client_secret":"", "oauth_scope":"", "oauth_token":"", "xsrf_token_url":"", "xsrf_token_header":"X-CSRF-Token"}'
    DESC: str = '''
        Send HTTP request (get/post/etc.) to request_url, process response via resp_fn, then store to value_key.
        Supports session persistence via session_key, built-in Basic Auth and OAuth authentication.

        - timeout: request timeout in seconds (default: 60)
        - session_key: key of data_chain to store/retrieve requests.Session for persistent connections (default: "__session_key")
        - resp_fn: Python function body string to process the response, variable "response" is available (default: "return response.text if response.status_code == 200 else response.status_code")
        - request_url: target URL for the HTTP request (supports expression)
        - headers: HTTP headers in "key[>value|key2[>value2" format (supports expression)
        - method: HTTP method, e.g. "get", "post", "put", "delete" (default: "get")
        - params: URL query parameters in "key[>value|key2[>value2" format (supports expression)
        - data_raw: raw request body as string (supports expression)
        - data: form data in "key[>value|key2[>value2" format (supports expression)
        - data_key: key of data_chain to get request body data from (takes priority over data param)
        - value_key: key of data_chain to store the processed response (supports expression)
        - verify: "yes" to enable SSL verification, "no" to bypass (default: "yes")
        - is_zip_response: "yes" to treat response as a zip file and extract contents, "no" to use resp_fn (default: "no")
        - filter_fn: when is_zip_response is "yes", Python function body string to filter zip entries by filename; parameter is 'filename', should return bool (default: "return True")
        - convert_fn: when is_zip_response is "yes", Python function body string to convert file bytes; parameter is 'file_content' (bytes), should return converted value (default: "return file_content.decode('utf-8')")
        - basic_auth_user: Basic Auth username (supports expression). When set with basic_auth_pwd, auto base64-encodes and sets Authorization header.
        - basic_auth_pwd: Basic Auth password (supports expression and encrypted values).
        - oauth_token_url: OAuth token endpoint URL. When set, fetches Bearer token via client_credentials grant. Token is cached in data_chain and reused until expired. (supports expression)
        - oauth_client_id: OAuth client_id (supports expression)
        - oauth_client_secret: OAuth client_secret (supports expression and encrypted values)
        - oauth_scope: OAuth scope, optional (supports expression)
        - oauth_token: dual-purpose: if oauth_token_url is set, serves as cache key for the fetched token; if oauth_token_url is not set, used directly as Bearer token value (supports expression)
        - xsrf_token_url: URL to fetch XSRF/CSRF token via GET request with "X-CSRF-Token: Fetch" header. Requires OAuth Bearer token from prior auth. Token is cached and attached to all subsequent requests. (supports expression)
        - xsrf_token_header: custom header name for the XSRF token (default: "X-CSRF-Token")

        Auth priority: OAuth > Basic Auth > manual Authorization header.
    '''

    _OAUTH2_EXPIRY_MARGIN_SECONDS = 30

    def get_category(self) -> str:
        return super().CATE_HTTP

    def process(self):

        request_url = self.expression2str(self.get_param('request_url'))
        value_key = self.expression2str(self.get_param('value_key'))
        timeout = int(self.explain_param_or_default('timeout', 60))

        headers: dict = {}
        params: dict = {}
        data = None

        if self.has_param('session_key'):
            session = self.get_data(self.get_param('session_key'))
            if session is None:
                session = requests.Session()
                self.populate_data(self.get_param('session_key'), session)
        else:
            session = requests.Session()

        if self.has_param('headers'):
            headers = self.str2dict(self.expression2str(self.get_param('headers')))

        if self.has_param('params'):
            params = self.str2dict(self.expression2str(self.get_param('params')))

        if self.has_param('data'):
            data = self.str2dict(self.expression2str(self.get_param('data')))

        if self.has_param('data_key'):
            data = self.get_data(self.get_param('data_key'))

        if self.has_param('data_raw'):
            data = self.expression2str(self.get_param('data_raw'))

        method = self.explain_param_or_default('method', 'get')
        verify = self.get_param('verify').lower() in ('y', 'yes', 'true', '1') if self.has_param('verify') else True

        logging.info('HTTP %s %s', method.upper(), request_url)
        logging.debug('req.headers - %s', headers)
        logging.debug('req.data - %s', data)
        logging.debug('req.params - %s', params)
        logging.debug('req.timeout - %s', timeout)

        if self.has_param('basic_auth_user') and self.has_param('oauth_token_url'):
            logging.warning('auth - Both basicAuth and oAuth configured; oAuth Bearer token will take precedence')

        self._apply_basic_auth(headers)
        self._apply_oauth2_auth(headers)
        self._apply_xsrf_token(headers)

        response = getattr(session, method)(request_url, timeout=(timeout, timeout), data=data, params=params,
                                            headers=headers, verify=verify)
        response.encoding = 'utf-8'

        self._update_xsrf_token_from_response(response)

        if response.status_code >= 400:
            logging.warning('resp.status_code - %s', response.status_code)
        else:
            logging.info('resp.status_code - %s', response.status_code)
        logging.debug('resp.headers - %s', response.headers)

        if self.has_param('is_zip_response') and self.get_param('is_zip_response') == 'yes':
            if response.ok:
                filter_body = self.explain_param_or_default('filter_fn', 'return True')
                convert_body = self.explain_param_or_default('convert_fn', "return file_content.decode('utf-8')")
                data_in_resp = self._extract_zip_to_dict(response, filter_body, convert_body)
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    logging.debug('resp.body - ' + str(response.content))
                    logging.debug('data_in_resp - ' + json.dumps(data_in_resp))
            else:
                logging.error(
                    f'ZIP response request failed, status_code={response.status_code}, '
                    f'reason={response.reason if response.reason else "unknown reason"}'
                )
                data_in_resp = {}

        else:
            resp_fun_body = self.explain_param_or_default('resp_fn', 'return response.text if response.status_code == 200 else response.status_code')

            data_in_resp = CodeExplainerUtil.create_and_execute_func('HTTP_REQUESTProcessor_process', '(response)',
                                                                     resp_fun_body, args=response)
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug('resp.text - ' + response.text)
                logging.debug('data_in_resp - ' + resp_fun_body)

        self.populate_data(value_key, data_in_resp)

    def _apply_basic_auth(self, headers: dict) -> None:
        if not self.has_param('basic_auth_user') or not self.has_param('basic_auth_pwd'):
            return

        user = self.expression2str(self.get_param('basic_auth_user'))
        pwd = self.expression2str(self.get_param('basic_auth_pwd'))
        credentials = f'{user}:{pwd}'
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('ascii')
        headers['Authorization'] = f'Basic {encoded}'
        logging.info('auth.basic - Applied Basic Auth for user: %s', user)

    def _apply_oauth2_auth(self, headers: dict) -> None:
        if self.has_param('oauth_token_url'):
            self._fetch_oauth2_token(headers)
        elif self.has_param('oauth_token'):
            token = self.expression2str(self.get_param('oauth_token'))
            headers['Authorization'] = f'Bearer {token}'
            logging.info('auth.oauth2 - Applied direct Bearer token')

    def _fetch_oauth2_token(self, headers: dict) -> None:
        token_url = self.expression2str(self.get_param('oauth_token_url'))
        client_id = self.expression2str(self.get_param('oauth_client_id'))
        client_secret = self.expression2str(self.get_param('oauth_client_secret'))
        scope = (self.expression2str(self.get_param('oauth_scope'))
                 if self.has_param('oauth_scope') else None)

        cache_key = self._get_oauth2_cache_key(token_url, client_id)

        cached = self.get_data(cache_key) if self.has_data(cache_key) else None
        if cached and time.monotonic() < cached['expires_at'] - self._OAUTH2_EXPIRY_MARGIN_SECONDS:
            remaining = cached['expires_at'] - time.monotonic()
            logging.info('auth.oauth2 - Using cached token (expires in %.0fs)', remaining)
            token_type = cached.get('token_type', 'Bearer')
            headers['Authorization'] = f'{token_type} {cached["access_token"]}'
            return

        logging.info('auth.oauth2 - Fetching new token from %s', token_url)
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        }
        if scope:
            token_data['scope'] = scope

        try:
            token_response = requests.post(token_url, data=token_data, timeout=30)
        except requests.RequestException as e:
            raise RuntimeError(f'auth.oauth2 - Token request failed: {e}') from e

        if not token_response.ok:
            error_body = token_response.text[:500]
            logging.error('auth.oauth2 - Token request failed: status=%d body=%s',
                          token_response.status_code, error_body)
            raise RuntimeError(
                f'auth.oauth2 - Token request failed with status {token_response.status_code}: {error_body}'
            )

        token_json = token_response.json()
        if 'access_token' not in token_json:
            raise RuntimeError(f'auth.oauth2 - Token response missing access_token: {token_json}')

        access_token = token_json['access_token']
        expires_in = int(token_json.get('expires_in', 3600))
        token_type = token_json.get('token_type', 'Bearer')
        token_type = token_type.title() if token_type else 'Bearer'

        token_cache = {
            'access_token': access_token,
            'expires_at': time.monotonic() + expires_in,
            'token_type': token_type,
        }
        self.task.data_chain[cache_key] = token_cache

        logging.info('auth.oauth2 - Token obtained, expires in %ds, cached as %s',
                     expires_in, cache_key)
        headers['Authorization'] = f'{token_type} {access_token}'

    @staticmethod
    def _get_oauth2_cache_key(token_url: str, client_id: str) -> str:
        raw = f'{token_url}|{client_id}'
        short_hash = hashlib.md5(raw.encode('utf-8')).hexdigest()[:12]
        return f'__oauth2_token__{short_hash}'

    _XSRF_CACHE_KEY = '__xsrf_token_cache'

    def _get_xsrf_header_name(self) -> str:
        if self.has_param('xsrf_token_header'):
            return self.expression2str(self.get_param('xsrf_token_header'))
        return 'X-CSRF-Token'

    def _apply_xsrf_token(self, headers: dict) -> None:
        if not self.has_param('xsrf_token_url'):
            return

        header_name = self._get_xsrf_header_name()
        cached = self.get_data(self._XSRF_CACHE_KEY) if self.has_data(self._XSRF_CACHE_KEY) else None
        if cached:
            headers[header_name] = cached
            logging.info('auth.xsrf - Using cached XSRF token')
            return

        token_url = self.expression2str(self.get_param('xsrf_token_url'))
        fetch_headers = {header_name: 'Fetch'}
        if 'Authorization' in headers:
            fetch_headers['Authorization'] = headers['Authorization']

        logging.info('auth.xsrf - Fetching XSRF token from %s', token_url)
        try:
            resp = requests.get(token_url, headers=fetch_headers, timeout=30)
        except requests.RequestException as e:
            raise RuntimeError(f'auth.xsrf - XSRF token fetch failed: {e}') from e

        if not resp.ok:
            raise RuntimeError(
                f'auth.xsrf - XSRF token fetch failed with status {resp.status_code}: {resp.text[:500]}'
            )

        token = resp.headers.get(header_name)
        if not token:
            raise RuntimeError(f'auth.xsrf - Response missing {header_name} header')

        self.task.data_chain[self._XSRF_CACHE_KEY] = token
        headers[header_name] = token
        logging.info('auth.xsrf - Token fetched and cached')

    def _update_xsrf_token_from_response(self, response) -> None:
        if not self.has_param('xsrf_token_url'):
            return

        header_name = self._get_xsrf_header_name()
        new_token = response.headers.get(header_name)
        if new_token and new_token != 'Required':
            old = self.get_data(self._XSRF_CACHE_KEY) if self.has_data(self._XSRF_CACHE_KEY) else None
            if new_token != old:
                self.task.data_chain[self._XSRF_CACHE_KEY] = new_token
                logging.info('auth.xsrf - Token refreshed from response header')

    def _extract_zip_to_dict(self, response, filter_func_body="return True",
                             convert_func_body="return file_content.decode('utf-8')"):
        """
        Extract files from a zip response, filtered by a dynamic function on filename,
        with configurable content conversion.

        :param response: HTTP response whose content is a zip file
        :param filter_func_body: Python function body string; parameter is 'filename', should return bool.
                                 Default: "return True" (keep all files)
                                 e.g. "return filename.endswith('.csv')"
        :param convert_func_body: Python function body string; parameter is 'file_content' (bytes),
                                  should return the converted value.
                                  Default: "return file_content.decode('utf-8')" (converts bytes to str)
                                  e.g. "import json\nreturn json.loads(file_content)"
        :return: dict {filename: converted_content} for files that pass the filter
        """
        filter_func = CodeExplainerUtil.create_and_execute_func(
            'HTTP_REQUESTProcessor_zip_filter', '(filename)', filter_func_body
        )
        convert_func = CodeExplainerUtil.create_and_execute_func(
            'HTTP_REQUESTProcessor_zip_convert', '(file_content)', convert_func_body
        )

        result = {}
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            for name in zf.namelist():
                if filter_func(name):
                    result[name] = convert_func(zf.read(name))
        return result
