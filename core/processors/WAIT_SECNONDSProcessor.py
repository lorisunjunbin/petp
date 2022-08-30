from core.processor import Processor

import time

class WAIT_SECNONDSProcessor(Processor):
    TPL: str = '{"wait_seconds":"5"}'
    DESC: str = f''' 
        {TPL}
    '''

    def process(self):
        wait_seconds = self.get_param('wait_seconds')
        time.sleep(int(wait_seconds))
