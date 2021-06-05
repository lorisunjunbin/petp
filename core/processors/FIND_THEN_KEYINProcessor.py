import logging

from selenium.webdriver.common.keys import Keys
from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class FIND_THEN_KEYINProcessor(Processor):
    TPL: str = '{"keyinby":"id|xpath|css", "identity":"", "value":"", "value_key":"", "clearb4keyin":"yes|no","wait":1}'
    DESC = f'''
    To call chrome driver find the element, then call send_key, simulate keyboard action, input string/press KEY_ENTER/etc.
    
    {TPL}
    
    "keyinby" is locator type
    "identity" is locator itself
    "value" is the given string or KEY_*
    "value_key" is property of data_chain, support nested access, '__m;author' means: data_chain['__m']['author']
    "clearb4keyin" is flag to decide whether clear before key in.
    "wait" is extra wait in seconds, after locating element, before key in.
    
    Supported keys: ['KEY_NULL', 'KEY_CANCEL', 'KEY_HELP', 'KEY_BACKSPACE', 'KEY_BACK_SPACE', 'KEY_TAB', 'KEY_CLEAR', 'KEY_RETURN', 'KEY_ENTER', 'KEY_SHIFT', 'KEY_LEFT_SHIFT', 'KEY_CONTROL', 'KEY_LEFT_CONTROL', 'KEY_ALT', 'KEY_LEFT_ALT', 'KEY_PAUSE', 'KEY_ESCAPE', 'KEY_SPACE', 'KEY_PAGE_UP', 'KEY_PAGE_DOWN', 'KEY_END', 'KEY_HOME', 'KEY_LEFT', 'KEY_ARROW_LEFT', 'KEY_UP', 'KEY_ARROW_UP', 'KEY_RIGHT', 'KEY_ARROW_RIGHT', 'KEY_DOWN', 'KEY_ARROW_DOWN', 'KEY_INSERT', 'KEY_DELETE', 'KEY_SEMICOLON', 'KEY_EQUALS', 'KEY_NUMPAD0', 'KEY_NUMPAD1', 'KEY_NUMPAD2', 'KEY_NUMPAD3', 'KEY_NUMPAD4', 'KEY_NUMPAD5', 'KEY_NUMPAD6', 'KEY_NUMPAD7', 'KEY_NUMPAD8', 'KEY_NUMPAD9', 'KEY_MULTIPLY', 'KEY_ADD', 'KEY_SEPARATOR', 'KEY_SUBTRACT', 'KEY_DECIMAL', 'KEY_DIVIDE', 'KEY_F1', 'KEY_F2', 'KEY_F3', 'KEY_F4', 'KEY_F5', 'KEY_F6', 'KEY_F7', 'KEY_F8', 'KEY_F9', 'KEY_F10', 'KEY_F11', 'KEY_F12', 'KEY_META', 'KEY_COMMAND'])
    '''
    def process(self):

        keyinby = self.get_param('keyinby')
        identity = self.get_param('identity')
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        ele = self.get_element_by(chrome, keyinby, identity)
        super().extra_wait()
        # to build chrome default support keys that match to selenium IDE recording.
        avaliable_keys = {}
        for key, val in SeleniumUtil.get_chrome_keys():
            attr_name = 'KEY_' + key
            expr = attr_name + '=Keys.%s' % key
            exec(expr)
            avaliable_keys[attr_name] = val
        # above is doing something like:
        KEY_NULL = Keys.NULL

#        logging.info(f"available keys: ${str(avaliable_keys.keys())}")

        if not ele is None:
            v: any

            if self.has_param('value_key'):
                v = self.get_deep_data(self.get_param('value_key').split(self.SEPARATOR))
            elif self.has_param('value'):
                v = eval("f'" + self.get_param('value') + "'")

            if (self.has_param('clearb4keyin')):
                if "yes" == self.get_param("clearb4keyin"):
                    ele.clear()

            logging.info(f"send_key: {v}")

            ele.send_keys(v)

        else:
            raise Exception(f'FIND_THEN_KEYINProcessor not able to find ele by: {identity}')
