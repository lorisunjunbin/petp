import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class FIND_THEN_KEYINProcessor(Processor):
    TPL: str = '{"find_by":"id|xpath|css", "identity":"", "value":"", "value_key":"", "clear_before_input":"yes|no","wait":1, "timeout":5, "skip_timeout_error":"yes|no", "chrome_name":"chrome"}'
    DESC = '''
    Call the Chrome driver to locate a web element, then simulate keyboard input via send_keys.
    Supports typing strings or pressing special keys (KEY_ENTER, KEY_TAB, etc.).

    - find_by: Locator strategy to find the element, one of: id, xpath, css (supports expression, default: "id|xpath|css")
    - identity: The locator value used to find the element (supports expression, default: "")
    - value: The string to type or a KEY_* constant to press (supports expression, default: "")
    - value_key: Key in data_chain to read the value from; supports nested access via ';' separator, e.g. '__m;author' means data_chain['__m']['author'] (supports expression, default: "")
    - clear_before_input: If "yes", clears the element's existing content before typing (supports expression, default: "yes|no")
    - wait: Extra wait time in seconds BEFORE locating the element — lets a still-rendering element (e.g. an Angular form just switched into via MOVE_TO_IFRAME) appear (supports expression, default: 1)
    - timeout: maximum seconds to wait for the element to appear (default: 5)
    - skip_timeout_error: whether to suppress the error when the element is not found within timeout. "yes" logs & returns silently (execution continues); "no" or absent → raise. (default: "yes|no")

    Supported keys: ['KEY_NULL', 'KEY_CANCEL', 'KEY_HELP', 'KEY_BACKSPACE', 'KEY_BACK_SPACE', 'KEY_TAB', 'KEY_CLEAR', 'KEY_RETURN', 'KEY_ENTER', 'KEY_SHIFT', 'KEY_LEFT_SHIFT', 'KEY_CONTROL', 'KEY_LEFT_CONTROL', 'KEY_ALT', 'KEY_LEFT_ALT', 'KEY_PAUSE', 'KEY_ESCAPE', 'KEY_SPACE', 'KEY_PAGE_UP', 'KEY_PAGE_DOWN', 'KEY_END', 'KEY_HOME', 'KEY_LEFT', 'KEY_ARROW_LEFT', 'KEY_UP', 'KEY_ARROW_UP', 'KEY_RIGHT', 'KEY_ARROW_RIGHT', 'KEY_DOWN', 'KEY_ARROW_DOWN', 'KEY_INSERT', 'KEY_DELETE', 'KEY_SEMICOLON', 'KEY_EQUALS', 'KEY_NUMPAD0', 'KEY_NUMPAD1', 'KEY_NUMPAD2', 'KEY_NUMPAD3', 'KEY_NUMPAD4', 'KEY_NUMPAD5', 'KEY_NUMPAD6', 'KEY_NUMPAD7', 'KEY_NUMPAD8', 'KEY_NUMPAD9', 'KEY_MULTIPLY', 'KEY_ADD', 'KEY_SEPARATOR', 'KEY_SUBTRACT', 'KEY_DECIMAL', 'KEY_DIVIDE', 'KEY_F1', 'KEY_F2', 'KEY_F3', 'KEY_F4', 'KEY_F5', 'KEY_F6', 'KEY_F7', 'KEY_F8', 'KEY_F9', 'KEY_F10', 'KEY_F11', 'KEY_F12', 'KEY_META', 'KEY_COMMAND'])
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):

        keyinby = self.get_param('find_by')
        identity = self.get_param('identity')
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')

        timeout = int(self.get_param('timeout')) if self.has_param('timeout') else 200
        skip_timeout_error = 'yes' == self.get_param('skip_timeout_error') \
            if self.has_param('skip_timeout_error') else False

        # Wait BEFORE locating (mirrors FIND_THEN_CLICK). The element may still be
        # rendering — e.g. an Angular form just switched into via MOVE_TO_IFRAME.
        # Waiting after locating is useless when the element isn't there yet.
        super().extra_wait()
        ele = SeleniumUtil.get_element_by(chrome, keyinby, identity, timeout)

        # to build chrome default support keys that match to selenium IDE recording.
        avaliable_keys = {f'KEY_{key}': val for key, val in SeleniumUtil.get_chrome_keys()}

        if not ele is None:
            v: any

            if self.has_param('value_key'):
                v = self.get_deep_data(self.get_param('value_key').split(self.SEPARATOR))
            elif self.has_param('value'):
                v = self.expression2str(self.get_param('value'))

            if (self.has_param('clear_before_input')):
                if "yes" == self.get_param("clear_before_input"):
                    ele.clear()

            logging.debug(f"send_key: {v}")

            ele.send_keys(avaliable_keys[v]
                          if v in avaliable_keys.keys()
                          else v)

        elif skip_timeout_error:
            logging.info('FIND_THEN_KEYIN find %s -> %s timeout: %s (skip_timeout_error=yes)',
                         keyinby, identity, timeout)
            return
        else:
            raise Exception(f'FIND_THEN_KEYINProcessor not able to find ele by: {identity}')
