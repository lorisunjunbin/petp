import io
import logging
import zipfile

import requests

from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil


class HTTP_REQUESTProcessor(Processor):
    TPL: str = '{"timeout":60, "session_key":"__session_key","resp_func_body":"return response.text if response.status_code == 200 else response.status_code", "request_url":"http://www.baidu.com", "headers":"header1[>value1|header2[>value2", "method":"get|post", "params":"pk1[>pv1|pk2[>pv2","data_raw":"","data":"dk1[>dv1|dk2[>dv2", "data_key":"", "value_key":"", "verify":"Y|N", "is_zip_response":"yes|no", "filter_func_body":"return True", "convert_func_body":"return file_content.decode(\'utf-8\')"}'
    DESC: str = f'''
        Send HTTP request (get/post/etc.) to request_url, process response via resp_func_body, then store to value_key.
        Supports session persistence via session_key.

        - timeout: request timeout in seconds (default: 60)
        - session_key: key of data_chain to store/retrieve requests.Session for persistent connections (default: "__session_key")
        - resp_func_body: Python function body string to process the response, variable "response" is available (default: "return response.text if response.status_code == 200 else response.status_code")
        - request_url: target URL for the HTTP request (supports expression)
        - headers: HTTP headers in "key[>value|key2[>value2" format (supports expression)
        - method: HTTP method, e.g. "get", "post", "put", "delete" (default: "get")
        - params: URL query parameters in "key[>value|key2[>value2" format (supports expression)
        - data_raw: raw request body as string (supports expression)
        - data: form data in "key[>value|key2[>value2" format (supports expression)
        - data_key: key of data_chain to get request body data from (takes priority over data param)
        - value_key: key of data_chain to store the processed response (supports expression)
        - verify: "Y" to enable SSL verification, "N" to bypass (default: "Y")
        - is_zip_response: "yes" to treat response as a zip file and extract contents, "no" to use resp_func_body (default: "no")
        - filter_func_body: when is_zip_response is "yes", Python function body string to filter zip entries by filename; parameter is 'filename', should return bool (default: "return True")
        - convert_func_body: when is_zip_response is "yes", Python function body string to convert file bytes; parameter is 'file_content' (bytes), should return converted value (default: "return file_content.decode('utf-8')")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_HTTP

    def process(self):

        request_url = self.expression2str(self.get_param('request_url'))
        value_key = self.expression2str(self.get_param('value_key'))
        timeout = self.get_param('timeout') if self.has_param('timeout') else 60

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
            headers.update(session.headers)
            headers = self.str2dict(self.expression2str(self.get_param('headers')))

        if self.has_param('params'):
            params = self.str2dict(self.expression2str(self.get_param('params')))

        if self.has_param('data'):
            data = self.str2dict(self.expression2str(self.get_param('data')))

        if self.has_param('data_key'):
            data = self.get_data(self.get_param('data_key'))

        if self.has_param('data_raw'):
            data = self.expression2str(self.get_param('data_raw'))

        method = self.get_param('method') if self.has_param('method') else 'get'
        verify = True if 'Y' == self.get_param('verify') else False

        logging.info('\n')
        logging.info('===============================================')

        response = getattr(session, method)(request_url, timeout=(timeout, timeout), data=data, params=params,
                                            headers=headers, verify=verify)
        response.encoding = 'utf-8'

        logging.info('<----------------------------------------------<')
        # response
        logging.info('resp.text - ' + response.text)
        logging.info('resp.status_code - ' + str(response.status_code))
        logging.info('resp.headers - ' + str(response.headers))
        logging.info('>---------------------------------------------->')
        # request
        logging.info('req.url - ' + request_url)
        logging.info('req.headers - ' + str(headers))
        logging.info('req.data - ' + str(data))
        logging.info('req.params - ' + str(params))
        logging.info('req.method - ' + method)
        logging.info('req.timeout - ' + str(timeout))
        logging.info('wait2connect.timeout - ' + str(timeout))
        logging.info('===============================================\n')

        if self.has_param('is_zip_response') and self.get_param('is_zip_response') == 'yes':
            filter_body = self.expression2str(self.get_param('filter_func_body')) if self.has_param(
                'filter_func_body') else 'return True'
            convert_body = self.expression2str(self.get_param('convert_func_body')) if self.has_param(
                'convert_func_body') else "return file_content.decode('utf-8')"
            data_in_resp = self._extract_zip_to_dict(response, filter_body, convert_body)

        else:
            resp_fun_body = self.expression2str(self.get_param('resp_func_body')) if self.has_param(
                'resp_func_body') else 'return response.text if response.status_code == 200 else response.status_code'

            data_in_resp = CodeExplainerUtil.create_and_execute_func('HTTP_REQUESTProcessor_process', '(response)',
                                                                     resp_fun_body, args=response)

        self.populate_data(value_key, data_in_resp)

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
