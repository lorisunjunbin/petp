from bs4 import BeautifulSoup

from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil

'''

pip install beautifulsoup4
pip install lxml

https://beautiful-soup-4.readthedocs.io/en/latest/

'''


class BEAUTIFUL_SOUPProcessor(Processor):
    TPL: str = '{"inbound_data_key":"", "inbound_data":"", "parser":"html.parser|xml", "outbound_data_key":"soup_outbound","func_body":"print(str(args.data)) print(str(args.soup))"}'

    DESC: str = f''' 
        - Collect data(outbound_data_key) from HTML/XML String via beautifulsoup4:
          https://beautiful-soup-4.readthedocs.io/en/latest/
          
        {TPL}
        
    '''

    def process(self):
        parser = self.get_param("parser")
        inbound_data = self.get_data_by_param_default_param('inbound_data_key', 'inbound_data')
        outbound_data_key = self.get_param("outbound_data_key")
        soup = BeautifulSoup(inbound_data, parser)
        resp = CodeExplainerUtil.func_wrapper_call('BEAUTIFUL_SOUPProcessor_process', '(soup)',
                                                   self.get_param("func_body"), soup)

        self.populate_data(outbound_data_key, resp)
