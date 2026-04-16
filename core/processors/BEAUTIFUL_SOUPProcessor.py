import logging

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
        Parse HTML or XML content using BeautifulSoup and execute a custom function body to extract data.
        The parsed soup object and raw data are available inside the function body for flexible processing.
        See: https://beautiful-soup-4.readthedocs.io/en/latest/

        - inbound_data_key: key in data_chain whose value is the HTML/XML string to parse; takes precedence over inbound_data (supports expression, default: "")
        - inbound_data: raw HTML/XML string to parse when inbound_data_key is not set (supports expression, default: "")
        - parser: BeautifulSoup parser to use, either "html.parser" or "xml" (default: "html.parser|xml")
        - outbound_data_key: key in data_chain to store the result returned by the function body (supports expression, default: "soup_outbound")
        - func_body: Python function body as a string; receives args.data (raw input) and args.soup (parsed object) (supports expression, default: "print(str(args.data)) print(str(args.soup))")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_HTTP

    def process(self):
        parser = self.get_param("parser")
        inbound_data = self.get_data_by_param_default_param('inbound_data_key', 'inbound_data')
        logging.debug(f"inbound_data: {inbound_data}")
        outbound_data_key = self.get_param("outbound_data_key")
        soup = BeautifulSoup(inbound_data, parser)
        resp = CodeExplainerUtil.create_and_execute_func('BEAUTIFUL_SOUPProcessor_process', '(soup, p)',
                                                         self.get_param("func_body"), soup, self)

        self.populate_data(outbound_data_key, resp)
