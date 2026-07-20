import logging
import time

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class SELECT_MULTI_DROPDOWNProcessor(Processor):
    TPL: str = '{"values":"value1,value2", "container_xpath":"", "expand_xpath":"", "item_class":"drop-down-menu-item-with-checkbox", "wait":1, "timeout":10, "skip_timeout_error":"yes|no", "close_xpath":"", "skip_if_fn":"return False", "chrome_name":"chrome"}'
    DESC: str = '''
        Select one or more options in a multi-select checkbox dropdown (e.g. SAP Ariba
        "供应商属性": 制造商 / 代理商 / 贸易商 ...). Opens the dropdown if needed, then checks
        each requested value. Option text is matched fuzzily (contains) and case-insensitively;
        already-checked options are left as-is (idempotent). Only the requested values are
        checked — existing selections are not cleared.

        - values: option texts to select, separated by "," or ">", e.g. "制造商,代理商". Each supports expression, e.g. "{types}". (required)
        - container_xpath: xpath scoping the dropdown widget; all lookups are scoped under it. Empty = whole page. Recommended: the field's input/container, e.g. "//input[@aria-label='供应商属性']/ancestor::div[contains(@class,'input-drop-down-container')]" (default: "")
        - expand_xpath: xpath (relative to container if container given, else absolute) of the element to click to OPEN the dropdown when options are not visible. Empty = auto (clicks an "expand_more" icon / the combobox input) (default: "")
        - item_class: CSS class marking each option row that carries the checkbox (default: "drop-down-menu-item-with-checkbox")
        - wait: seconds to sleep before starting (default: 1)
        - timeout: max seconds to wait for the dropdown / options to appear (default: 10)
        - skip_timeout_error: "yes" logs & continues when an option is not found or a click fails; "no" raises (default: "yes|no")
        - close_xpath: xpath of an element to click LAST to CLOSE the dropdown after selecting. A relative xpath (starting with ".") is scoped to container_xpath (so it targets THIS dropdown's collapse icon, not an outer panel's); absolute xpath is used as-is. Empty = leave the dropdown as-is. Supports expression. (default: "")
        - skip_if_fn: Python function body receiving (p); return True to SKIP this whole processor before locating anything (e.g. when its values are built from a data_chain value that may be absent). Default runs the processor. (default: "return False")
        - chrome_name: key in data_chain holding the Chrome driver (default: "chrome")
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    _UP = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _LO = 'abcdefghijklmnopqrstuvwxyz'

    def _item_xpath(self, container, item_class, text):
        """Xpath of an option row whose visible text CONTAINS ``text``
        (fuzzy + case-insensitive), scoped under ``container``."""
        lit = SeleniumUtil.xpath_literal(text.lower())
        fold = "translate(normalize-space(),'%s','%s')" % (self._UP, self._LO)
        row = ("*[contains(concat(' ',normalize-space(@class),' '),' %s ') and contains(%s,%s) and .//span[contains(@class,'display-icon')]]"
               % (item_class, fold, lit))
        base = container if container else ''
        return "%s//%s" % (base, row)

    def process(self):
        super().process()
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')

        raw = self.get_param('values')
        if isinstance(raw, list):
            parts = [self.expression2str(str(s)) for s in raw]
        else:
            resolved = self.expression2str(str(raw))
            parts = [self.expression2str(p) for p in resolved.replace('>', ',').split(',')]
        values = [p.strip() for p in parts if p and p.strip()]
        if not values:
            raise Exception('SELECT_MULTI_DROPDOWN: values must resolve to at least one text')

        container = self.explain_param_or_default('container_xpath', '') or ''
        timeout = int(self.get_param('timeout')) if self.has_param('timeout') else 10
        item_class = self.explain_param_or_default('item_class', 'drop-down-menu-item-with-checkbox')
        skip_err = self.get_param_bool_if_equal('skip_timeout_error', 'yes')

        super().extra_wait()

        self._ensure_open(chrome, container, item_class, values[0], timeout)

        for text in values:
            ok = self._select_option_js(chrome, container, item_class, text)
            logging.info('SELECT_MULTI_DROPDOWN: select %r -> %s', text, ok)
            if ok not in ('checked', 'already'):
                if not skip_err:
                    raise Exception('SELECT_MULTI_DROPDOWN: failed to select %r (%s)' % (text, ok))
                logging.info('SELECT_MULTI_DROPDOWN: %r not selected (%s, skip)', text, ok)

        # Optionally close the dropdown after selecting. Empty close_xpath =
        # leave it as-is. explain_optional returns '' for an unresolved "{var}".
        close_xpath = self.explain_optional('close_xpath', '')
        if close_xpath:
            self._close_dropdown(chrome, container, close_xpath)

    def _close_dropdown(self, chrome, container, close_xpath):
        """Click the element that closes the dropdown after selecting.

        A relative close_xpath (starting with '.') is scoped to the container —
        same as _ensure_open — so it targets THIS dropdown's collapse icon, not
        the first matching icon on the page (which could collapse an outer
        panel). Absolute xpath is used as-is. Native click first, then move-to,
        then JS as fallback.
        """
        if container and close_xpath.startswith('.'):
            xp = container + close_xpath[1:]   # container + "//..." (valid xpath)
        else:
            xp = close_xpath
        eles = SeleniumUtil.find_elements_by_x_path(chrome, xp)
        if not eles:
            logging.info('SELECT_MULTI_DROPDOWN: close button not found: %r', xp)
            return
        result = SeleniumUtil.click_with_fallback(chrome, eles[0])
        logging.info('SELECT_MULTI_DROPDOWN: close via %r -> %s', xp, result)

    def _select_option_js(self, chrome, container, item_class, text):
        """Select one option atomically, in the browser.

        Does everything in a single execute_script so there are no stale Python
        element references and no scroll-induced row mixups: find the row whose
        visible text contains ``text`` (case-insensitive), scroll it into view,
        and — only if its checkbox is not already checked — click the checkbox
        icon ONCE. Returns 'checked' | 'already' | 'not-found' | 'no-icon'.
        The row selector uses the configured item_class; the checkbox icon is
        found by a fixed CSS selector, expressed in JS to keep it atomic.
        """
        js = r"""
        var container = arguments[0], itemClass = arguments[1], want = (arguments[2]||'').toLowerCase();
        var root = container ? document.evaluate(container, document, null, 9, null).singleNodeValue : document;
        if (!root) return 'not-found';
        var rows = root.querySelectorAll('.' + itemClass);
        for (var i = 0; i < rows.length; i++) {
            var row = rows[i];
            var icon = row.querySelector('.display-icon md-icon, .display-icon .material-icons');
            if (!icon) continue;               // inner text span also has itemClass; skip rows w/o an icon
            var txt = (row.textContent || '').trim().toLowerCase();
            if (txt.indexOf(want) === -1) continue;
            row.scrollIntoView({block:'center'});
            var state = (icon.textContent || '').trim();
            if (state === 'check_box') return 'already';
            icon.click();
            return 'checked';
        }
        return 'not-found';
        """
        try:
            return chrome.execute_script(js, container, item_class, text)
        except Exception as ex:
            logging.debug('SELECT_MULTI_DROPDOWN: _select_option_js error: %s', ex)
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
        """Open the dropdown, then confirm its options are actually visible.

        Always clicks the expand control first (the expand_more icon), because
        the options DOM is present-but-hidden until opened. After clicking,
        confirm by DOM PRESENCE of an option row (via _find_item) — more
        reliable than Selenium visibility on virtual-scroller nodes.
        """
        if self._item_present(chrome, container, item_class, first_text):
            return   # already open (option row present in DOM)
        # Candidates that may toggle the dropdown open. The expand-more icon is
        # the primary trigger for this widget; the combobox input is a fallback
        # for other widgets. A user-supplied expand_xpath is tried first.
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
            # Try NATIVE ele.click() first (same as FIND_THEN_CLICK, which is
            # confirmed to open this widget), then fall back to the
            # scrollIntoView/ActionChains/JS-click helper. Some Ariba controls
            # respond to native click but NOT to the JS-dispatched click.
            try:
                eles[0].click()
            except Exception:
                try:
                    SeleniumUtil.move_to_ele_then_click(chrome, eles[0])
                except Exception as ex:
                    logging.debug('SELECT_MULTI_DROPDOWN: expand click on %s failed: %s', cand, type(ex).__name__)
                    continue
            # Confirm by DOM PRESENCE of an option row (visibility is unreliable
            # on the virtual-scroller). Give it a short poll.
            if self._find_item(chrome, container, item_class, first_text, min(timeout, 4)) is not None:
                logging.info('SELECT_MULTI_DROPDOWN: dropdown opened via %s', cand)
                return
            logging.debug('SELECT_MULTI_DROPDOWN: %s did not open the dropdown, trying next', cand)
        logging.info('SELECT_MULTI_DROPDOWN: dropdown may not have opened; proceeding anyway')

    def _item_present(self, chrome, container, item_class, first_text):
        """True if an option row is present in the DOM (not necessarily visible)."""
        try:
            return bool(SeleniumUtil.find_elements_by_x_path(
                chrome, self._item_xpath(container, item_class, first_text)))
        except Exception:
            return False
