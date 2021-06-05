from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class MOVE_TO_IFRAMEProcessor(Processor):
    TPL: str = '{"frame_ids":["at least give one"]}'
    DESC: str = f''' 
        Move to specific iframe, support multiple iframes. 

        {TPL}

    '''
    def process(self):
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        SeleniumUtil.move_to_target_frame(chrome, self.get_param('frame_ids'))
