from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class MOVE_TO_IFRAMEProcessor(Processor):
    TPL: str = '{"frame_ids":["at least give one"], "chrome_name":"chrome"}'
    DESC: str = f'''
        Switch chrome driver context into specific iframe, supports nested iframes by providing multiple frame IDs.

        - frame_ids: list of frame identifiers (index, name or id) to navigate through, e.g. ["frame1", "frame2"]

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        SeleniumUtil.move_to_target_frame(chrome, self.get_param('frame_ids'))
