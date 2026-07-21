import logging
import time

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class SELECT_SINGLE_DROPDOWNProcessor(Processor):
    TPL: str = '{"value":"option text", "container_xpath":"", "expand_xpath":"", "item_class":"type-ahead-list-item", "wait":1, "timeout":10, "skip_timeout_error":"yes|no", "skip_if_fn":"return False", "chrome_name":"chrome"}'
    DESC: str = '''
        Select ONE option in a single-select type-ahead dropdown (e.g. SAP Ariba
        "企业注册性质": 国企 / 私企 / 有限责任公司 ...). Opens the dropdown if needed, finds the
        option row whose visible text matches (fuzzy contains, case-insensitive) and clicks it once.
        The list closes itself after the click (single-select), so no close step is needed.

        - value: the option text to select, e.g. "国企" (supports expression, e.g. "{kind}"). If several comma-separated texts are given only the first is used. (required)
        - container_xpath: xpath scoping the dropdown widget; all lookups are scoped under it. Empty = whole page. Recommended: the field's input/container, e.g. "//input[@aria-label='企业注册性质']/ancestor::div[contains(@class,'input-drop-down-container')]" (default: "")
        - expand_xpath: xpath (relative to container if container given, else absolute) of the element to click to OPEN the dropdown when options are not visible. Empty = auto (clicks an "expand_more" icon / the combobox input) (default: "")
        - item_class: CSS class marking each option row (default: "type-ahead-list-item")
        - wait: seconds to sleep before starting (default: 1)
        - timeout: max seconds to wait for the dropdown / options to appear (default: 10)
        - skip_timeout_error: "yes" logs & continues when the option is not found or the click fails; "no" raises (default: "yes|no")
        - skip_if_fn: Python function body receiving (p); return True to SKIP this whole processor before locating anything (e.g. when value is built from a data_chain value that may be absent). Default runs the processor. (default: "return False")
        - chrome_name: key in data_chain holding the Chrome driver (default: "chrome")
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    _UP = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _LO = 'abcdefghijklmnopqrstuvwxyz'

    def _item_xpath(self, container, item_class, text):
        """Xpath of an option row whose visible text CONTAINS ``text``
        (fuzzy + case-insensitive), scoped under ``container``. Unlike the
        multi-select variant there is no checkbox-icon requirement — a
        single-select option row is a plain text node."""
        lit = SeleniumUtil.xpath_literal(text.lower())
        fold = "translate(normalize-space(),'%s','%s')" % (self._UP, self._LO)
        row = ("*[contains(concat(' ',normalize-space(@class),' '),' %s ') and contains(%s,%s)]"
               % (item_class, fold, lit))
        base = container if container else ''
        return "%s//%s" % (base, row)

    def process(self):
        super().process()
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')

        raw = self.get_param('value')
        if isinstance(raw, list):
            parts = [self.expression2str(str(s)) for s in raw]
        else:
            resolved = self.expression2str(str(raw))
            parts = [p for p in resolved.replace('>', ',').split(',')]
        candidates = [p.strip() for p in parts if p and p.strip()]
        if not candidates:
            raise Exception('SELECT_SINGLE_DROPDOWN: value must resolve to a non-empty text')
        value = candidates[0]
        if len(candidates) > 1:
            logging.info('SELECT_SINGLE_DROPDOWN: multiple values given, using first only: %r', value)

        container = self.explain_param_or_default('container_xpath', '') or ''
        timeout = int(self.get_param('timeout')) if self.has_param('timeout') else 10
        item_class = self.explain_param_or_default('item_class', 'type-ahead-list-item')
        skip_err = self.get_param_bool_if_equal('skip_timeout_error', 'yes')

        super().extra_wait()

        self._ensure_open(chrome, container, item_class, value, timeout)

        # Make sure the target row is in the DOM (virtual-scroller may need a
        # nudge), then click it once via atomic JS.
        if self._find_item(chrome, container, item_class, value, timeout) is None:
            msg = 'SELECT_SINGLE_DROPDOWN: option not found: %r' % value
            if skip_err:
                self.log_noop('option %r NOT found -- NOT selected (skip_timeout_error=yes)' % value)
                return
            raise Exception(msg)

        result = self._select_item_js(chrome, container, item_class, value)
        logging.info('SELECT_SINGLE_DROPDOWN: select %r -> %s', value, result)
        if result != 'clicked':
            if skip_err:
                self.log_noop('option %r NOT selected (%s, skip_timeout_error=yes)' % (value, result))
                return
            raise Exception('SELECT_SINGLE_DROPDOWN: failed to select %r (%s)' % (value, result))

    def _select_item_js(self, chrome, container, item_class, text):
        """Click the option row atomically, in the browser: find the row whose
        visible text contains ``text`` (case-insensitive), scroll it into view,
        and click it ONCE. Single-select rows carry no checkbox, so this just
        clicks the row. Returns 'clicked' | 'not-found'."""
        js = r"""
        var container = arguments[0], itemClass = arguments[1], want = (arguments[2]||'').toLowerCase();
        var root = container ? document.evaluate(container, document, null, 9, null).singleNodeValue : document;
        if (!root) return 'not-found';
        var rows = root.querySelectorAll('.' + itemClass);
        for (var i = 0; i < rows.length; i++) {
            var txt = (rows[i].textContent || '').trim().toLowerCase();
            if (txt.indexOf(want) === -1) continue;
            rows[i].scrollIntoView({block:'center'});
            rows[i].click();
            return 'clicked';
        }
        return 'not-found';
        """
        try:
            return chrome.execute_script(js, container, item_class, text)
        except Exception as ex:
            logging.debug('SELECT_SINGLE_DROPDOWN: _select_item_js error: %s', ex)
            return 'error'

    def _find_item(self, chrome, container, item_class, text, timeout):
        """Find an option by text, PRESENT in the DOM.

        The options live in an Angular virtual-scroller that only renders the
        rows currently in view — a target further down is NOT in the DOM until
        the list is scrolled to it. So: check present; if absent, scroll the
        scroll-container down step by step (re-checking each step); if still
        absent, scroll back to the top and step down from there. Selenium
        visibility is unreliable here, so we only test DOM PRESENCE.
        """
        xp = self._item_xpath(container, item_class, text)
        scroller_xp = (container + "//*[contains(@class,'scrollable-content') or "
                       "contains(@class,'total-padding')]/..") if container else \
                      "//*[contains(@class,'scrollable-content')]/.."
        # First a short presence wait (list may still be rendering).
        deadline = time.time() + max(1, timeout)
        while time.time() < deadline:
            eles = SeleniumUtil.find_elements_by_x_path(chrome, xp)
            if eles:
                return eles[0]
            time.sleep(0.3)
        # Not visible yet — scroll the virtual-scroller to render more rows.
        scrollers = SeleniumUtil.find_elements_by_x_path(chrome, scroller_xp)
        if not scrollers:
            return None
        scroller = scrollers[0]
        try:
            chrome.execute_script("arguments[0].scrollTop = 0;", scroller)
        except Exception:
            pass
        for _ in range(40):   # bounded steps; small list
            eles = SeleniumUtil.find_elements_by_x_path(chrome, xp)
            if eles:
                return eles[0]
            try:
                prev = chrome.execute_script("return arguments[0].scrollTop;", scroller)
                chrome.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].clientHeight;", scroller)
                now = chrome.execute_script("return arguments[0].scrollTop;", scroller)
            except Exception:
                break
            if now == prev:      # reached the bottom, no more to render
                eles = SeleniumUtil.find_elements_by_x_path(chrome, xp)
                return eles[0] if eles else None
            time.sleep(0.2)
        return None

    def _ensure_open(self, chrome, container, item_class, first_text, timeout):
        """Open the dropdown, then confirm its options are actually present.

        Clicks the expand control first (the expand_more icon / combobox input),
        because the options DOM is present-but-hidden until opened. After
        clicking, confirm by DOM PRESENCE of an option row (via _find_item) —
        more reliable than Selenium visibility on virtual-scroller nodes.
        """
        if self._item_present(chrome, container, item_class, first_text):
            return   # already open (option row present in DOM)
        expand = self.explain_param_or_default('expand_xpath', '')
        candidates = ([expand] if expand else []) + [
            ".//i[contains(@class,'expand-more-icon')]",
            ".//i[contains(@class,'material-icons') and normalize-space()='expand_more']",
            ".//input[@role='combobox']",
            ".//input[contains(@class,'input-form-field')]",
        ]
        for cand in candidates:
            if not cand:
                continue
            if container and cand.startswith('.'):
                xp = container + cand[1:]     # container + "//..." (valid xpath)
            else:
                xp = cand
            eles = SeleniumUtil.find_elements_by_x_path(chrome, xp)
            if not eles:
                continue
            SeleniumUtil.click_with_fallback(chrome, eles[0])
            if self._find_item(chrome, container, item_class, first_text, min(timeout, 4)) is not None:
                logging.info('SELECT_SINGLE_DROPDOWN: dropdown opened via %s', cand)
                return
            logging.debug('SELECT_SINGLE_DROPDOWN: %s did not open the dropdown, trying next', cand)
        logging.info('SELECT_SINGLE_DROPDOWN: dropdown may not have opened; proceeding anyway')

    def _item_present(self, chrome, container, item_class, first_text):
        """True if an option row is present in the DOM (not necessarily visible)."""
        try:
            return bool(SeleniumUtil.find_elements_by_x_path(
                chrome, self._item_xpath(container, item_class, first_text)))
        except Exception:
            return False
