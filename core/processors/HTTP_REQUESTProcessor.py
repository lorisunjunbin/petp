import logging

import requests

from core.processor import Processor


class HTTP_REQUESTProcessor(Processor):
    TPL: str = '{"request_url":"http://www.baidu.com", "headers":"header1=value1;header2=value2", "method":"get|post", "data":"key1=value1;key2=value2", "data_key":"", "value_key":""}'
    DESC: str = f''' 
        - Send http request(get | post) to request_url, populate response to value_key 

        {TPL}

    '''

    def process(self):

        request_url = self.expression2str(self.get_param('request_url'))
        value_key = self.expression2str(self.get_param('value_key'))

        headers: dict = {}
        response = None

        if self.has_param('headers'):
            headers = self.str2dict(self.get_param('headers'))

        if self.get_param('method') == 'get':
            response = requests.get(request_url, headers=headers)

        if self.get_param('method') == 'post':
            data = self.get_data(self.get_param('data_key')) if self.has_param('data_key') else \
                self.str2dict(self.get_param('data'))

            response = requests.post(request_url, data=data, headers=headers)

            logging.info('response.headers:' + str(response.headers))

        if response.status_code == 200:
            logging.info(f'r.text: {response.text}')
            self.populate_data(value_key, response.text)
        else:
            logging.warning(response.status_code)
