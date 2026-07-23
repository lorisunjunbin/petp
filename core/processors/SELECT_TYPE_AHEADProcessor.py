import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class SELECT_TYPE_AHEADProcessor(Processor):
    TPL: str = '{"aria_label":"国家/地区", "value":"中国", "option_class":"mat-option", "wait":1, "timeout":10, "skip_timeout_error":"yes|no", "skip_if_fn":"return False", "chrome_name":"chrome"}'
    DESC: str = '''
        Select ONE option in a SAP Ariba type-ahead / md-autocomplete field (e.g. 国家/地区, 州/省/地区,
        or any single-value autocomplete): the ``value`` is typed into the input located by its
        aria-label, then the popup option whose visible text EXACTLY equals ``value`` is clicked — or,
        if none matches exactly, the UNIQUE option that CONTAINS it (so a province typed as "辽宁"
        matches the listed "辽宁(070)", while "中国" is picked exactly rather than "中立区"/"中非共和国").
        This wraps the shared SeleniumUtil.select_type_ahead used by the bank/contact feeders, so a
        single autocomplete field can be filled on its own without a whole feeder.

        - aria_label: aria-label of the type-ahead input, e.g. "国家/地区". Supports expression, e.g. "{field}". (required)
        - value: the option text to select, e.g. "中国". Supports expression, e.g. "{country}". (required)
        - option_class: CSS class of each autocomplete option row in the popup (default: "mat-option")
        - wait: seconds to sleep before starting, lets the form finish rendering (default: 1)
        - timeout: max seconds to wait for the input / option panel to appear (default: 10)
        - skip_timeout_error: "yes" logs & continues when the field/option is not found; "no" raises (default: "yes|no")
        - skip_if_fn: Python function body receiving (p); return True to SKIP this whole processor before locating anything (e.g. when value is built from a data_chain value that may be absent). Default runs the processor. (default: "return False")
        - chrome_name: key in data_chain holding the Chrome driver (default: "chrome")
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):
        super().process()
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')

        aria_label = self.expression2str(str(self.get_param('aria_label'))).strip()
        if not aria_label:
            raise Exception('SELECT_TYPE_AHEAD: aria_label is required')
        value = self.expression2str(str(self.get_param('value'))).strip()
        if not value:
            raise Exception('SELECT_TYPE_AHEAD: value must resolve to a non-empty text')

        option_class = self.explain_param_or_default('option_class', 'mat-option')
        timeout = int(self.get_param('timeout')) if self.has_param('timeout') else 10
        skip_err = self.get_param_bool_if_equal('skip_timeout_error', 'yes')

        super().extra_wait()

        ok = SeleniumUtil.select_type_ahead(chrome, aria_label, option_class, value, timeout)
        logging.info('SELECT_TYPE_AHEAD: %r <- %r -> %s', aria_label, value, 'clicked' if ok else 'not-selected')
        if not ok:
            self.fail_or_skip('option %r not selected for %r' % (value, aria_label), skip_err,
                              prefix='SELECT_TYPE_AHEAD')
