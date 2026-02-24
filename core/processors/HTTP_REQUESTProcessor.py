import logging

import requests

from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil


class HTTP_REQUESTProcessor(Processor):
    TPL: str = '{"timeout":60, "session_key":"__session_key","resp_func_body":"return response.text if response.status_code == 200 else response.status_code", "request_url":"http://www.baidu.com", "headers":"header1[>value1|header2[>value2", "method":"get|post", "params":"pk1[>pv1|pk2[>pv2","data_raw":"","data":"dk1[>dv1|dk2[>dv2", "data_key":"", "value_key":"", "verify":"Y|N"}'
    DESC: str = f'''
        - Send http request(get | post | etc.) to request_url, populate response to value_key, support session.
        - verify: control SSL certificate verification (default: true), set to false to bypass SSL check for expired certificates.

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
            headers = self.str2dict(self.expression2str(self.get_param('headers')))
            headers.update(session.headers)

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

        response = getattr(session, method)(request_url, timeout=(5, timeout), data=data, params=params,
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
        logging.info('===============================================\n')

        data_in_resp = CodeExplainerUtil.create_and_execute_func('HTTP_REQUESTProcessor_process', '(response)',
                                                                 self.get_param("resp_func_body"), args=response)

        self.populate_data(value_key, data_in_resp)
