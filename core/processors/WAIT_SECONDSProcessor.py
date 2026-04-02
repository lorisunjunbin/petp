from core.processor import Processor

import time


class WAIT_SECONDSProcessor(Processor):
    TPL: str = '{"wait_seconds":"5"}'
    DESC: str = f'''
        Pause execution for the given number of seconds.

        - wait_seconds: number of seconds to wait (default: "5")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_GENERAL

    def process(self):
        wait_seconds = self.get_param('wait_seconds')
        time.sleep(int(wait_seconds))
