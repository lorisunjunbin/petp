import logging
import os

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class FILE_UPLOADProcessor(Processor):
    TPL: str = '{"identity":"", "file_path":"", "reveal_hidden":"yes|no", "wait":1, "timeout":30, "skip_timeout_error":"yes|no", "skip_if_fn":"return False", "chrome_name":"chrome"}'
    DESC: str = '''
        Upload a file to an <input type="file"> by sending the file's absolute path to it — the standard
        WebDriver way, bypassing the OS file-chooser dialog. Works with HIDDEN file inputs (e.g. Angular
        "上载文件" widgets whose real input is class="hidden ..."): unlike FIND_THEN_KEYIN this waits for
        the element's PRESENCE, not visibility (a hidden input is never "visible", so a visibility wait
        would always time out), and can optionally strip the element's hidden state first.

        - identity: xpath of the file input, e.g. "//sm-questionnaire-item[.//span[contains(.,'7.2')]]//input[@type='file']" (supports expression) (required)
        - file_path: ABSOLUTE path of the file to upload; must exist on the machine running PETP (the browser reads it locally). Supports expression, e.g. "{attached_sales_performance}" (required)
        - reveal_hidden: "yes" runs a small JS to remove the 'hidden'/'hidden-input' class and clear display:none on the input before uploading (some setups reject send_keys to a fully hidden input); "no" leaves it as-is (default: "yes|no")
        - wait: seconds to sleep before starting (default: 1)
        - timeout: max seconds to wait for the file input to be PRESENT in the DOM (default: 30)
        - skip_timeout_error: "yes" logs & returns when the input is not found or the file is missing; "no" raises (default: "yes|no")
        - skip_if_fn: Python function body receiving (p); return True to SKIP this whole processor before locating anything (default: "return False")
        - chrome_name: key in data_chain holding the Chrome driver (default: "chrome")
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):
        super().process()
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')

        identity = self.explain_param_or_default('identity', '')
        file_path = self.explain_param_or_default('file_path', '')
        reveal = self.get_param_bool_if_equal('reveal_hidden', 'yes')
        timeout = int(self.get_param('timeout')) if self.has_param('timeout') else 30
        skip_err = self.get_param_bool_if_equal('skip_timeout_error', 'yes')

        if not identity:
            raise Exception('FILE_UPLOAD: identity (xpath of the file input) is required')
        if not file_path:
            raise Exception('FILE_UPLOAD: file_path is required')

        # The browser reads the file from the machine running this driver — send
        # an absolute path and fail early (before send_keys) if it's missing, so
        # the error says "file missing" rather than a cryptic webdriver one.
        abs_path = os.path.abspath(os.path.expanduser(file_path))
        if not os.path.isfile(abs_path):
            return self.fail_or_skip('file does not exist: %r (resolved %r)' % (file_path, abs_path), skip_err)

        super().extra_wait()

        # Wait for PRESENCE only — a hidden file input is never "visible", so a
        # visibility wait (what FIND_THEN_KEYIN uses) would always time out.
        if SeleniumUtil.wait_for_element_xpath_presence(chrome, identity, timeout) is None:
            return self.fail_or_skip('file input not present: %r' % identity, skip_err)
        eles = SeleniumUtil.find_elements_by_x_path(chrome, identity)
        if not eles:
            return self.fail_or_skip('file input not found: %r' % identity, skip_err)
        ele = eles[0]

        if reveal:
            # Some widgets keep the real input hidden; a few browsers reject
            # send_keys to a display:none input. Strip the common hidden markers.
            try:
                chrome.execute_script(
                    "arguments[0].classList.remove('hidden');"
                    "arguments[0].classList.remove('hidden-input');"
                    "arguments[0].style.display='block';"
                    "arguments[0].style.visibility='visible';"
                    "arguments[0].removeAttribute('hidden');", ele)
            except Exception as ex:
                logging.debug('FILE_UPLOAD: reveal-hidden JS failed (non-fatal): %s', ex)

        try:
            ele.send_keys(abs_path)
        except Exception as ex:
            return self.fail_or_skip('send_keys failed: %s' % type(ex).__name__, skip_err)
        logging.info('FILE_UPLOAD: uploaded %r via %r', abs_path, identity)

