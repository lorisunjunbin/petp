from core.processor import Processor
from httpservice.HttpServer import HttpRequestHandler


class HTTP_RESPONSE_KEYProcessor(Processor):
	TPL: str = '{"http_response_key":"result"}'

	DESC: str = f''' 

        This is required if you want call PETP from http service, 
        It will read data from the data_chain based on the http_response_key and use it as the HTTP response body.
        
        {TPL}

    '''

	def get_category(self) -> str:
		return super().CATE_DATA_PROCESSING

	def process(self):
		key = self.get_param('http_response_key')
		self.populate_data(HttpRequestHandler.get_response_key(), key)
