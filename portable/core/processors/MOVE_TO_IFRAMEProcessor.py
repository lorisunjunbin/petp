import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class MOVE_TO_IFRAMEProcessor(Processor):
    TPL: str = '{"frame_ids":["at least give one"], "wait":1, "timeout":10, "skip_timeout_error":"yes|no", "chrome_name":"chrome"}'
    DESC: str = '''
        Switch chrome driver context into specific iframe, supports nested iframes by providing multiple frame IDs.

        - frame_ids: list of frame identifiers (index, name or id) to navigate through, e.g. ["frame1", "frame2"].
          Two sentinels move OUT instead of into a frame: "$default$" switches back to the top-level document,
          "$parent$" switches to the parent frame (one level up). They can be mixed with real ids,
          e.g. ["$default$"] to return to the main document, or ["$default$", "SMFrame"] to reset then re-enter.
        - wait: seconds to sleep before attempting to switch frame — lets the iframe finish rendering (default: 1)
        - timeout: maximum seconds to wait for EACH iframe element to become visible before switching (default: 10)
        - skip_timeout_error: when an iframe is not visible within ``timeout`` — "yes" logs & returns silently
          (chrome driver kept alive, execution continues); "no" raises. Default: "no"
        - chrome_name: key in data_chain holding the Chrome driver (default: "chrome")
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        frame_ids = self.get_param('frame_ids')
        timeout = int(self.get_param('timeout')) if self.has_param('timeout') else 10
        skip_timeout_error = 'yes' == self.get_param('skip_timeout_error') \
            if self.has_param('skip_timeout_error') else False

        super().extra_wait()

        logging.debug('Moving to iframe: %s (timeout=%ds)', frame_ids, timeout)
        result = SeleniumUtil.move_to_target_frame(chrome, frame_ids, timeout=timeout)
        if result is None:
            msg = f'MOVE_TO_IFRAME: failed to switch into {frame_ids} within {timeout}s'
            if skip_timeout_error:
                logging.info('%s (skip_timeout_error=yes)', msg)
                return
            raise Exception(msg)
