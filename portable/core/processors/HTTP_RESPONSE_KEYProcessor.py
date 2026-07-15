import logging

from core.processor import Processor
from core.constants import HTTP_RESPONSE_KEY


class HTTP_RESPONSE_KEYProcessor(Processor):
    TPL: str = '{"http_response_key":"result"}'

    DESC: str = ''' 

        Required when calling PETP from an HTTP service. Specifies which data chain key's value should be used
        as the HTTP response body. The processor reads data from the data chain using the given key and registers
        it as the response key for the HTTP handler.

        - http_response_key: The data chain key whose value will be returned as the HTTP response body (supports expression, default: "result")

    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        key = self.expression2str(self.get_param('http_response_key'))
        logging.debug('HTTP response key set to: %s', key)
        self.populate_data(HTTP_RESPONSE_KEY, key)
