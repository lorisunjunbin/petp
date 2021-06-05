import logging

from core.processor import Processor


class UNKNOWN_TASKProcessor(Processor):
    TPL: str = '{"msg":""}'

    DESC: str = f'''
        This is empty task, only should be used when converting Selenium IDE recording to PETP execution.
        
        {TPL}
    '''

    def process(self):
        logging.warning('UNKNOWN_TASK!!! ' + self.get_param("msg"))
