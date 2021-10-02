import logging

import requests

from core.processor import Processor


class HTTP_REQUESTProcessor(Processor):
    TPL: str = '{"request_url":"http://www.baidu.com", "headers":"header1->value1|header2->value2", "method":"get|post", "params":"pk1->pv1|pk2->pv2","data_raw":"","data":"dk1->dv1|dk2->dv2", "data_key":"", "value_key":""}'
    DESC: str = f''' 
        - Send http request(get | post) to request_url, populate response to value_key 

        {TPL}

    '''

    def process(self):

        request_url = self.expression2str(self.get_param('request_url'))
        value_key = self.expression2str(self.get_param('value_key'))

        headers: dict = {}
        params: dict = {}
        data = None
        response = None

        if self.has_param('params'):
            params = self.str2dict(self.expression2str(self.get_param('params')))

        if self.has_param('data'):
            data = self.str2dict(self.expression2str(self.get_param('data')))

        if self.has_param('data_key'):
            data = self.get_data(self.get_param('data_key'))

        if self.has_param('data_raw'):
            data = self.expression2str(self.get_param('data_raw'))

        if self.has_param('headers'):
            headers = self.str2dict(self.expression2str(self.get_param('headers')))

        logging.info('\n')
        logging.info('----------------------------------------------')
        logging.info('request.url - ' + request_url)
        logging.info('request.headers - ' + str(headers))
        logging.info('request.data - ' + str(data))
        logging.info('request.params - ' + str(params))

        if self.get_param('method') == 'get':
            response = requests.get(request_url, headers=headers, params=params, verify=False)

        if self.get_param('method') == 'post':
            response = requests.post(request_url, headers=headers, data=data, params=params, verify=False)

        logging.info('response.status_code - ' + str(response.status_code))
        logging.info('response.headers - ' + str(response.headers))
        logging.info('response.text - ' + response.text)
        logging.info('----------------------------------------------\n')

        if response.status_code == 200:
            response.encoding = 'utf-8'
            logging.info(f'r.text: {response.text}')
            self.populate_data(value_key, response.text)
        else:
            logging.warning(response.status_code)
