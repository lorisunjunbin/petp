import logging
import time

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class SELECT_TREE_DROPDOWNProcessor(Processor):
    TPL: str = '{"selections":"level1>level2>last level", "open_xpath":"", "close_xpath":"", "select_last":"yes|no", "check_from_level":1, "container_xpath":"//smq-browse-lists", "entry_class":"browse-entry", "pane_tag":"browse-pane", "text_class":"wrapped-text-content", "checked_state":"check_box", "wait":1, "timeout":10, "skip_timeout_error":"yes|no", "skip_if_fn":"return False", "chrome_name":"chrome"}'
    DESC: str = '''
        Drive a SAP Ariba cascading tree dropdown (smq-browse-lists / browse-pane / browse-entry).
        Given an ordered list of option texts (1..8 levels), it expands each level by clicking the
        entry's ">" arrow (expansion-btn) and checks the final level's checkbox. Option text is matched
        FUZZILY (contains), so a partial keyword is enough; located by visible text (.wrapped-text-content),
        scoped to the tree container.

        - selections: ">"-separated level texts, outer level first, e.g. "支持和服务>海外>亚太>迪拜院". 1 to 8 levels. Each level is matched fuzzily (partial keyword ok). Supports expression, e.g. "{level1}>{level2}" or a whole "{path}". (A list is also accepted for backward compatibility.) (required)
        - open_xpath: absolute xpath of a button/element to click FIRST to OPEN the dropdown (the tree container appears only after this click). Empty = assume already open, skip this step. After clicking, waits for the first level's text to appear in the DOM. Supports expression. (default: "")
        - close_xpath: absolute xpath of a button/element to click LAST to CLOSE the dropdown after selecting (often the same toggle button as open_xpath). Empty = leave the dropdown as-is. Supports expression. (default: "")
        - select_last: "yes" clicks the LAST level's checkbox to select it; "no" only expands it (default: "yes|no")
        - check_from_level: 1-based level from which entries get their checkbox checked; levels before it are only expanded, not checked. e.g. with "All>油气新能源>科研业务>迪拜院", 1 checks all (incl. All), 2 leaves All unchecked and checks the rest (default: 1)
        - container_xpath: xpath of the tree widget root; all lookups are scoped under it (default: "//smq-browse-lists")
        - entry_class: CSS class marking each option node (default: "browse-entry")
        - pane_tag: tag/selector of each level column, used for pane-scoped disambiguation (default: "browse-pane")
        - text_class: CSS class of the element carrying an option's visible text (default: "wrapped-text-content")
        - checked_state: icon text value that means "checked" (default: "check_box")
        - wait: seconds to sleep before starting, lets the widget finish rendering (default: 1)
        - timeout: max seconds to wait for each level's entry / next pane to appear (default: 10)
        - skip_timeout_error: "yes" logs & returns silently when a level's text is not found or a click is intercepted; "no" raises (default: "yes|no")
        - skip_if_fn: Python function body receiving (p); return True to SKIP this whole processor before locating anything (e.g. when its selections are built from a data_chain value that may be absent). Default runs the processor. (default: "return False")
        - chrome_name: key in data_chain holding the Chrome driver (default: "chrome")
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    # NOTE on `root` resolution used inside the JS helpers below:
    # container_xpath may match several elements (label wrappers, the button,
    # the real list container), the wrong one, or none. So each helper iterates
    # ALL xpath matches and picks the first that CONTAINS a paneTag; if none do
    # (or container is empty/wrong) it falls back to the outermost element that
    # holds panes anywhere on the page, else document. This makes container_xpath
    # a hint, not a hard requirement — fixing the "container matched but
    # paneCount:0" / "container:false" failures.

    def _find_entry(self, chrome, container, i, text, timeout):
        """Return True if the level-i entry is present, scoped to its pane column.

        The tree renders one ``pane_tag`` column per level side by side, so the
        level-i (0-based) entry lives in the (i+1)-th pane. Presence is checked
        by DOM existence (see _wait_entry_present) rather than Selenium
        visibility — the dropdown container is aria-hidden and Selenium's
        visibility wait times out even when the entry is in the DOM. Callers
        only need "is it there?", not the WebElement itself: expand and check
        both act via pane-scoped atomic JS.
        """
        return self._wait_entry_present(chrome, container, i + 1, text, timeout)

    def _select_checkbox(self, chrome, container, i, text, timeout, skip_err):
        """Check the entry's checkbox atomically, in the browser.

        Done in a single execute_script so there is no re-location, no stale
        reference, and — crucially — no second click: the old two-candidate
        Python loop could click the (already-selected) checkbox a second time
        and TOGGLE IT BACK OFF (the "it unchecks what was just checked" bug,
        same root cause as SELECT_MULTI's earlier rewrite). Here we find the
        level-i entry in its pane column, read the icon state, and click the
        checkbox ONCE only if not already in checked_state.
        Returns 'checked' | 'already' | 'not-found' | 'no-icon'.
        """
        c = self._cfg
        # Ensure the entry exists (waits on the pane-scoped locator) before the
        # atomic JS, so we honour timeout / skip_timeout_error consistently.
        if not self._find_entry(chrome, container, i, text, timeout):
            if skip_err:
                self.log_noop('level %r NOT found -- NOT checked (skip_timeout_error=yes)' % text)
                return False
            raise Exception('SELECT_TREE_DROPDOWN: failed to check checkbox for %r (not found)' % text)

        result = self._check_entry_js(
            chrome, container, c['pane_tag'], i + 1, c['entry_class'],
            c['text_class'], text, c['checked_state'])
        logging.info('SELECT_TREE_DROPDOWN: check %r (pane %d) -> %s', text, i + 1, result)
        if result in ('checked', 'already'):
            return True
        if skip_err:
            self.log_noop('level %r NOT checked (%s, skip_timeout_error=yes)' % (text, result))
            return False
        raise Exception('SELECT_TREE_DROPDOWN: failed to check checkbox for %r (%s)' % (text, result))

    def _check_entry_js(self, chrome, container, pane_tag, pane_index,
                        entry_class, text_class, text, checked_state):
        """Atomically find the level entry in its pane column and click its
        checkbox icon ONCE if not already checked."""
        js = r"""
        var container = arguments[0], paneTag = arguments[1], paneIndex = arguments[2];
        var entryClass = arguments[3], textClass = arguments[4];
        var want = (arguments[5] || '').trim().toLowerCase(), checked = arguments[6];
        var root = null;
        if (container) {
            var it = document.evaluate(container, document, null, 7, null);
            for (var k = 0; k < it.snapshotLength; k++) {
                var cand = it.snapshotItem(k);
                if (cand.querySelector(paneTag)) { root = cand; break; }
            }
            if (!root && it.snapshotLength > 0) root = it.snapshotItem(0);
        }
        if (!root || !root.querySelector(paneTag)) {
            var anyPane = document.querySelector(paneTag);
            if (anyPane) {
                var anc = anyPane;
                while (anc.parentElement && anc.parentElement.querySelector(paneTag)) anc = anc.parentElement;
                root = anc;
            }
        }
        if (!root) root = document;
        if (!root) return 'not-found';
        var panes = root.querySelectorAll(paneTag);
        if (panes.length < paneIndex) return 'not-found';
        var pane = panes[paneIndex - 1];
        var entries = pane.querySelectorAll('.' + entryClass);
        for (var i = 0; i < entries.length; i++) {
            var entry = entries[i];
            var tnode = entry.querySelector('.' + textClass);
            var txt = ((tnode ? tnode.textContent : entry.textContent) || '').trim().toLowerCase();
            if (txt.indexOf(want) === -1) continue;
            var icon = entry.querySelector('.display-icon md-icon, .display-icon .material-icons');
            if (!icon) return 'no-icon';
            entry.scrollIntoView({block: 'center'});
            var state = (icon.textContent || '').trim();
            if (state === checked) return 'already';
            icon.click();
            return 'checked';
        }
        return 'not-found';
        """
        try:
            return chrome.execute_script(
                js, container, pane_tag, pane_index, entry_class, text_class, text, checked_state)
        except Exception as ex:
            logging.debug('SELECT_TREE_DROPDOWN: _check_entry_js error: %s', ex)
            return 'error'

    def _expand_entry_js(self, chrome, container, pane_tag, pane_index,
                         entry_class, text_class, text):
        """Atomically find the level entry in its pane column and click its
        expansion arrow to open the next level.

        Same reason as _check_entry_js: an ActionChains-based click misses
        entries that need scrolling inside their pane column (L1/L2 at
        the top expand fine, but a deeper row that must scroll into view gets
        clicked at the wrong coordinates and the child pane never renders).
        Doing scrollIntoView + click in one browser-side call avoids that.
        Returns 'expanded' | 'not-found' | 'no-arrow'.
        """
        js = r"""
        var container = arguments[0], paneTag = arguments[1], paneIndex = arguments[2];
        var entryClass = arguments[3], textClass = arguments[4];
        var want = (arguments[5] || '').trim().toLowerCase();
        var root = null;
        if (container) {
            var it = document.evaluate(container, document, null, 7, null);
            for (var k = 0; k < it.snapshotLength; k++) {
                var cand = it.snapshotItem(k);
                if (cand.querySelector(paneTag)) { root = cand; break; }
            }
            if (!root && it.snapshotLength > 0) root = it.snapshotItem(0);
        }
        if (!root || !root.querySelector(paneTag)) {
            var anyPane = document.querySelector(paneTag);
            if (anyPane) {
                var anc = anyPane;
                while (anc.parentElement && anc.parentElement.querySelector(paneTag)) anc = anc.parentElement;
                root = anc;
            }
        }
        if (!root) root = document;
        if (!root) return 'not-found';
        var panes = root.querySelectorAll(paneTag);
        if (panes.length < paneIndex) return 'not-found';
        var pane = panes[paneIndex - 1];
        var entries = pane.querySelectorAll('.' + entryClass);
        for (var i = 0; i < entries.length; i++) {
            var entry = entries[i];
            var tnode = entry.querySelector('.' + textClass);
            var txt = ((tnode ? tnode.textContent : entry.textContent) || '').trim().toLowerCase();
            if (txt.indexOf(want) === -1) continue;
            entry.scrollIntoView({block: 'center'});
            var arrow = entry.querySelector('.expansion-btn');
            if (!arrow) return 'no-arrow';
            arrow.click();
            return 'expanded';
        }
        return 'not-found';
        """
        try:
            return chrome.execute_script(
                js, container, pane_tag, pane_index, entry_class, text_class, text)
        except Exception as ex:
            logging.debug('SELECT_TREE_DROPDOWN: _expand_entry_js error: %s', ex)
            return 'error'

    def _entry_present_js(self, chrome, container, pane_tag, pane_index,
                          entry_class, text_class, text):
        """Return True if the pane column contains an entry whose text matches.

        Pure DOM existence check — deliberately does NOT use Selenium's
        visibility judgement. The Ariba dropdown container is aria-hidden and
        rendered such that Selenium's wait_for_*_visible times out even though
        the entry is present in the DOM (the "XPath matches in lxml but the
        browser wait times out" symptom). Matching here uses the same
        textContent.indexOf logic as _check_entry_js / _expand_entry_js, so
        presence and action agree.
        """
        js = r"""
        var container = arguments[0], paneTag = arguments[1], paneIndex = arguments[2];
        var entryClass = arguments[3], textClass = arguments[4];
        var want = (arguments[5] || '').trim().toLowerCase();
        var root = null;
        if (container) {
            var it = document.evaluate(container, document, null, 7, null);
            for (var k = 0; k < it.snapshotLength; k++) {
                var cand = it.snapshotItem(k);
                if (cand.querySelector(paneTag)) { root = cand; break; }
            }
            if (!root && it.snapshotLength > 0) root = it.snapshotItem(0);
        }
        if (!root || !root.querySelector(paneTag)) {
            var anyPane = document.querySelector(paneTag);
            if (anyPane) {
                var anc = anyPane;
                while (anc.parentElement && anc.parentElement.querySelector(paneTag)) anc = anc.parentElement;
                root = anc;
            }
        }
        if (!root) root = document;
        if (!root) return false;
        var panes = root.querySelectorAll(paneTag);
        if (panes.length < paneIndex) return false;
        var pane = panes[paneIndex - 1];
        var entries = pane.querySelectorAll('.' + entryClass);
        for (var i = 0; i < entries.length; i++) {
            var tnode = entries[i].querySelector('.' + textClass);
            var txt = ((tnode ? tnode.textContent : entries[i].textContent) || '').trim().toLowerCase();
            if (txt.indexOf(want) !== -1) return true;
        }
        return false;
        """
        try:
            return bool(chrome.execute_script(
                js, container, pane_tag, pane_index, entry_class, text_class, text))
        except Exception as ex:
            logging.debug('SELECT_TREE_DROPDOWN: _entry_present_js error: %s', ex)
            return False

    def _wait_entry_present(self, chrome, container, pane_index, text, timeout):
        """Poll _entry_present_js until True or timeout (seconds). DOM-existence
        based, so it works where Selenium's visibility wait times out."""
        c = self._cfg
        deadline = time.monotonic() + max(0, timeout)
        while True:
            if self._entry_present_js(chrome, container, c['pane_tag'], pane_index,
                                      c['entry_class'], c['text_class'], text):
                return True
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.3)

    def _open_dropdown(self, chrome, open_xpath, container, first_text, timeout):
        """Click the (absolute-located) button that opens the tree dropdown,
        then wait for the first level's text to appear in the DOM.

        The open button lives OUTSIDE the tree container (the container only
        renders after the click), so it is located absolutely. This Angular
        Material div[role=button] responds to a NATIVE click but often NOT to a
        JS-dispatched .click() — the same quirk SELECT_MULTI._ensure_open guards
        against, and why the independent FIND_THEN_CLICK (native click) could
        open it while a JS click could not. So: native click first, then the
        move-to/ActionChains helper, then a JS click as last resort.

        The open button is a TOGGLE (click opens, click again closes). So if the
        dropdown is ALREADY open (first level present in the DOM) we must NOT
        click — that would close it. This also makes it safe when a separate
        FIND_THEN_CLICK already opened the dropdown before this task.
        """
        c = self._cfg
        if self._entry_present_js(chrome, container, c['pane_tag'], 1,
                                  c['entry_class'], c['text_class'], first_text):
            logging.info('SELECT_TREE_DROPDOWN: dropdown already open, skip open click')
            return
        eles = SeleniumUtil.find_elements_by_x_path(chrome, open_xpath)
        if not eles:
            logging.info('SELECT_TREE_DROPDOWN: open button not found: %r', open_xpath)
        else:
            result = SeleniumUtil.click_with_fallback(chrome, eles[0])
            logging.info('SELECT_TREE_DROPDOWN: open via %r -> %s', open_xpath, result)
        # Wait for the tree's first level to render (DOM presence, not Selenium
        # visibility). If it never appears, the existing PASS 1 logic will handle
        # "first level not found" per skip_timeout_error.
        self._wait_entry_present(chrome, container, 1, first_text, timeout)

    def _close_dropdown(self, chrome, close_xpath):
        """Click the (absolute-located) button that closes the dropdown after
        selecting — usually the same toggle button as open_xpath. Uses the
        native-then-fallback click (this Angular widget needs the native click).
        No 'already closed' guard: after selecting we always want it closed.
        """
        eles = SeleniumUtil.find_elements_by_x_path(chrome, close_xpath)
        if not eles:
            logging.info('SELECT_TREE_DROPDOWN: close button not found: %r', close_xpath)
            return
        result = SeleniumUtil.click_with_fallback(chrome, eles[0])
        logging.info('SELECT_TREE_DROPDOWN: close via %r -> %s', close_xpath, result)

    def process(self):
        super().process()
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        raw = self.get_param('selections')
        # selections is normally a ">"-separated string, e.g.
        #   "支持和服务>海外>亚太>迪拜院"
        # (a list is still accepted for backward compatibility). Each level (or
        # the whole string) supports expressions, e.g. "{path}" or "{l1}>{l2}".
        if isinstance(raw, list):
            parts = [self.expression2str(str(s)) for s in raw]
        else:
            resolved = self.expression2str(str(raw))
            parts = [self.expression2str(p) for p in resolved.split('>')]
        selections = [p.strip() for p in parts if p and p.strip()]
        if not (1 <= len(selections) <= 8):
            raise Exception('SELECT_TREE_DROPDOWN: selections must resolve to 1..8 ">"-separated texts')

        container = self.explain_param_or_default('container_xpath', '//smq-browse-lists')
        timeout = int(self.get_param('timeout')) if self.has_param('timeout') else 10
        select_last = ('yes' == self.get_param('select_last')) if self.has_param('select_last') else True
        check_from = int(self.get_param('check_from_level')) if self.has_param('check_from_level') else 1
        skip_err = self.get_param_bool_if_equal('skip_timeout_error', 'yes')

        # DOM-specific selectors — default to SAP Ariba's tree widget, overridable
        # for other cascading-tree widgets.
        self._cfg = {
            'entry_class':    self.explain_param_or_default('entry_class', 'browse-entry'),
            'pane_tag':       self.explain_param_or_default('pane_tag', 'browse-pane'),
            'text_class':     self.explain_param_or_default('text_class', 'wrapped-text-content'),
            'checked_state':  self.explain_param_or_default('checked_state', 'check_box'),
        }

        super().extra_wait()

        # Optionally open the dropdown first (its button lives outside the tree
        # container; empty open_xpath = assume already open). explain_optional
        # returns '' for an unresolved "{var}", so a missing dynamic value also
        # skips the open step.
        open_xpath = self.explain_optional('open_xpath', '')
        if open_xpath:
            self._open_dropdown(chrome, open_xpath, container, selections[0], timeout)

        n = len(selections)

        # PASS 1 — expand every level top→bottom, WITHOUT checking. In this tree
        # a checkbox click on a parent collapses/re-renders its child pane, so
        # interleaving expand and check breaks the cascade (child pane never
        # appears, and the wrong row ends up checked). Expanding fully first
        # keeps the cascade intact.
        for i, text in enumerate(selections):
            level = i + 1
            is_last = (i == n - 1)
            if not self._find_entry(chrome, container, i, text, timeout):
                msg = 'SELECT_TREE_DROPDOWN: level %d text not found: %r' % (level, text)
                if skip_err:
                    self.log_noop('level %d text %r NOT found -- selection ABORTED, '
                                  'remaining levels NOT expanded/checked (skip_timeout_error=yes)'
                                  % (level, text))
                    return
                raise Exception(msg)
            if is_last:
                continue
            # One pane column per level: the reliable "expanded" signal is the
            # NEXT level's entry appearing in pane i+2. Presence is a DOM check
            # (not Selenium visibility — the container is aria-hidden). Skip the
            # click if already rendered; otherwise click this entry's ">" arrow
            # (atomic JS — scrollIntoView + click in the browser, so a deep row
            # that must scroll into its pane still gets its arrow clicked; the
            # old ActionChains missed such rows and the child pane never
            # rendered) and wait for the next level to appear.
            nxt_present = self._entry_present_js(
                chrome, container, self._cfg['pane_tag'], i + 2,
                self._cfg['entry_class'], self._cfg['text_class'], selections[i + 1])
            if not nxt_present:
                c = self._cfg
                result = self._expand_entry_js(
                    chrome, container, c['pane_tag'], i + 1, c['entry_class'],
                    c['text_class'], text)
                logging.info('SELECT_TREE_DROPDOWN: expand %r (pane %d) -> %s', text, i + 1, result)
                self._wait_entry_present(chrome, container, i + 2, selections[i + 1], timeout)


        # PASS 2 — now that the whole path is expanded, check each level from
        # check_from_level to the last (the last also respects select_last).
        # Check SHALLOWEST→deepest (low level → high level): this widget keeps
        # child panes intact when a parent is checked, and the observed correct
        # order is parent-first.
        for i in range(n):
            level = i + 1
            is_last = (i == n - 1)
            should_check = level >= check_from and (select_last or not is_last)
            if should_check:
                self._select_checkbox(chrome, container, i, selections[i], timeout, skip_err)

        # Optionally close the dropdown (often the same toggle button as
        # open_xpath). Empty close_xpath = leave it open. explain_optional
        # returns '' for an unresolved "{var}", so a missing value also skips.
        close_xpath = self.explain_optional('close_xpath', '')
        if close_xpath:
            self._close_dropdown(chrome, close_xpath)
