import logging

from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil
from utils.SeleniumUtil import SeleniumUtil


class FIND_THEN_CLICKProcessor(Processor):
    TPL: str = '{"find_by":"id|xpath|link|css", "identity":"","identity_key":"", "wait":5, "timeout":5, "skip_timeout_error":"yes|no", "timeout_msg":"", "condition_fn":"return True", "skip_if_fn":"return False", "chrome_name":"chrome"}'

    DESC: str = '''
        Find a web element via Selenium using the specified locator strategy and click it.
        If the element is not found within the timeout, an exception is raised unless skip_timeout_error is set.

        - find_by: locator strategy to find the element, one of "id", "xpath", "link", or "css" (default: "id|xpath|link|css")
        - identity: the locator value used to find the element (supports expression, default: "")
        - identity_key: key in data_chain whose value is used as the locator; takes precedence over identity (supports expression, default: "")
        - wait: seconds to wait before performing the click action (default: 5)
        - timeout: maximum seconds to wait for the element to appear (default: 5)
        - skip_timeout_error: whether to suppress errors when the click cannot happen. "yes" swallows both
          "element not found within timeout" AND "element found but click intercepted / not clickable"
          (useful for conditional buttons like an error-dialog "ignore & submit"). "no" or absent → raise. (default: "yes|no")
        - timeout_msg: optional business message appended to the raised exception when the element is not
          found / not clickable AND skip_timeout_error is "no". Gives the hard failure domain context.
          Supports expression against data_chain AND the special {timeout} variable, e.g.
          "Can not find the supplier {supplier_name} in {timeout} seconds." Ignored when skip_timeout_error
          is "yes". (default: "")
        - condition_fn: Python function body; receives (ele) where ele is the located WebElement;
          click is only performed when the function returns True (default: "return True")
        - skip_if_fn: Python function body receiving (p); return True to SKIP this whole processor
          before locating anything (e.g. when its xpath is built from a data_chain value that may be
          absent). Default runs the processor. (default: "return False")
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):

        super().process()

        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        clickby = self.get_param('find_by')
        identity = self.get_data(self.get_param('identity_key')) if self.has_param('identity_key') \
            else self.expression2str(self.get_param('identity'))

        timeout = int(self.get_param('timeout')) if self.has_param('timeout') else 200
        skip_timeout_error = 'yes' == self.get_param('skip_timeout_error') \
            if self.has_param("skip_timeout_error") else False

        super().extra_wait()

        ele = SeleniumUtil.get_element_by(chrome, clickby, identity, timeout)
        if ele is None:
            if skip_timeout_error:
                self.log_noop('element not found within %ss: %s -> %s (skip_timeout_error=yes) — CLICK NOT PERFORMED'
                              % (timeout, clickby, identity))
                return
            else:
                msg = 'element not found within %ss: %s -> %s' % (timeout, clickby, identity)
                self.fail_or_skip(msg, False, prefix='FIND_THEN_CLICK',
                                  timeout_msg=self.resolve_timeout_msg(timeout))

        condition_body = self.explain_param_or_default('condition_fn', 'return True')
        condition_fn = CodeExplainerUtil.create_and_execute_func('FIND_THEN_CLICK_condition', '(p,ele)', condition_body)
        if not condition_fn(self, ele):
            self.log_noop('condition_fn returned False — CLICK NOT PERFORMED: %s' % identity)
            return

        try:
            ele.click()
            logging.debug('click: ' + identity)
        except Exception as ex:
            # Native click failed (commonly ElementClickInterceptedException). Try
            # the hover-then-click fallback; this is a routine recovery path, not
            # a red flag — log at DEBUG so operators don't see a huge stacktrace
            # for every recoverable case.
            logging.debug('move to click: %s (native click failed: %s)',
                          identity, type(ex).__name__)
            try:
                SeleniumUtil.move_to_ele_then_click(chrome, ele)
            except Exception as ex2:
                # Element found but not clickable (intercepted / covered by overlay /
                # detached / etc.). Same semantic as "timeout — element not there":
                # if the caller opted into ``skip_timeout_error='yes'``, treat this
                # as a soft-skip too and let the pipeline continue.
                if skip_timeout_error:
                    # Log the class name of the underlying error but NOT the
                    # multi-KB webdriver stacktrace — the intent ("skipped
                    # because unclickable") is what matters here.
                    self.log_noop('click intercepted/unclickable, skip_timeout_error=yes — CLICK NOT PERFORMED: %s -> %s (%s)'
                                  % (clickby, identity, type(ex2).__name__))
                    return
                self.fail_or_skip('click intercepted/unclickable: %s -> %s (%s)'
                                  % (clickby, identity, type(ex2).__name__),
                                  False, prefix='FIND_THEN_CLICK',
                                  timeout_msg=self.resolve_timeout_msg(timeout))
