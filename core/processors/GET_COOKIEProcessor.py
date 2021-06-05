import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class GET_COOKIEProcessor(Processor):
    TPL: str = '{"chrome_name":"chrome", "cookie_name":"", "value_key":"", "get_all":"no|yes"}'
    DESC: str = f''' 
        - to get cookie from chrome driver and popluate to value_key of data_chain 
        
        {TPL}
        
    '''

    def process(self):

        if (self.has_data(self.get_param('chrome_name'))):
            chrome = self.get_data(self.get_param('chrome_name'))
            value_key = self.expression2str(self.get_param("value_key"))

            if SeleniumUtil.is_web_driver(chrome):
                get_all = self.get_param("get_all")
                if 'yes' == get_all:
                    all_cookies = chrome.get_cookies()
                    logging.info('all cookies' + str(all_cookies))

                    all_cookies_str:str = ''
                    for c in all_cookies:
                        all_cookies_str += c['name'] + '='+c['value']+'; '

                    if len(all_cookies_str) > 0:
                        self.populate_data(value_key, all_cookies_str)
                        logging.info(f'populate {value_key} -> all_cookies_str -> {all_cookies_str}')

                else:
                    cookie_name = self.expression2str(self.get_param("cookie_name"))
                    cookie_value = chrome.get_cookie(cookie_name)
                    if len(cookie_value) > 0:

                        self.populate_data(value_key, cookie_value)
                        logging.info(f'populate {value_key} -> {cookie_name} = {cookie_value}')

