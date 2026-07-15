import json
import logging
import os

from core.processor import Processor
from utils.OSUtils import OSUtils


class DUMP_DOMProcessor(Processor):
    TPL: str = '{"file_path":"", "screenshot":"yes|no", "list_inputs":"yes|no", "wait":1, "chrome_name":"chrome"}'
    DESC: str = '''
        Debug helper: dump the CURRENT frame's DOM so you can inspect why a locator
        fails (especially in headless mode). Writes the current frame's full HTML to
        a file, optionally saves a screenshot, and logs every <input> in the current
        frame with its aria-label / id / name / visibility. Insert it right before a
        FIND_THEN_* task that cannot locate its element.

        - file_path: where to write the frame HTML (supports expression). Default:
          <download_dir>/dump_dom.html. A sibling .png is used for the screenshot.
        - screenshot: "yes" to also save a screenshot next to the HTML (default: "yes")
        - list_inputs: "yes" to log all <input> elements (aria-label/id/name/visible) (default: "yes")
        - wait: extra wait in seconds before dumping — lets the frame finish rendering (default: 1)
        - chrome_name: key in data_chain holding the Chrome driver (default: "chrome")

        {"file_path":"", "screenshot":"yes|no", "list_inputs":"yes|no", "wait":1, "chrome_name":"chrome"}
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        super().extra_wait()

        fp = self.expression2str(self.get_param('file_path')) if self.has_param('file_path') \
            and self.get_param('file_path') else os.path.join(self.get_ddir(), 'dump_dom.html')
        OSUtils.create_folder_if_not_existed(os.path.dirname(fp))

        do_shot = self.get_param('screenshot') != 'no' if self.has_param('screenshot') else True
        do_inputs = self.get_param('list_inputs') != 'no' if self.has_param('list_inputs') else True

        try:
            logging.info('[DUMP_DOM] current URL: %s', chrome.current_url)
            logging.info('[DUMP_DOM] viewport: %s',
                         chrome.execute_script('return [window.innerWidth, window.innerHeight]'))
        except Exception as e:
            logging.info('[DUMP_DOM] url/viewport unavailable: %s', e)

        # full HTML of the CURRENT frame context
        try:
            html = chrome.page_source
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(html)
            logging.info('[DUMP_DOM] frame HTML (%d bytes) -> %s', len(html), fp)
            self.populate_data('dump_dom_html_path', fp)
        except Exception as e:
            logging.warning('[DUMP_DOM] failed to dump HTML: %s', e)

        if do_shot:
            shot = os.path.splitext(fp)[0] + '.png'
            try:
                chrome.save_screenshot(shot)
                logging.info('[DUMP_DOM] screenshot -> %s', shot)
                self.populate_data('dump_dom_screenshot_path', shot)
            except Exception as e:
                logging.warning('[DUMP_DOM] failed to screenshot: %s', e)

        if do_inputs:
            try:
                inputs = chrome.execute_script("""
                    return Array.from(document.querySelectorAll('input')).map(function(el){
                      return {ariaLabel: el.getAttribute('aria-label'), id: el.id,
                              name: el.getAttribute('name'), type: el.type,
                              visible: !!(el.offsetWidth||el.offsetHeight||el.getClientRects().length)};
                    });
                """)
                logging.info('[DUMP_DOM] %d <input> in current frame:', len(inputs))
                for i, el in enumerate(inputs):
                    logging.info('[DUMP_DOM]   [%d] %s', i, json.dumps(el, ensure_ascii=False))
            except Exception as e:
                logging.warning('[DUMP_DOM] failed to list inputs: %s', e)
