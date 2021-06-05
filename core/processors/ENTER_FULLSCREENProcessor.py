from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class ENTER_FULLSCREENProcessor(Processor):
    TPL: str = '{"chrome_name":"chrome"}'
    DESC: str = f''' 
        - Make chrome browser to fullscreen mode associated with chrome_name which saved to data_chain. 
        
       {TPL}       
       
    '''

    def process(self):
        if (self.has_data(self.get_param('chrome_name'))):
            chrome = self.get_data(self.get_param('chrome_name'))
            if SeleniumUtil.is_web_driver(chrome):
                SeleniumUtil.full_screen(chrome)