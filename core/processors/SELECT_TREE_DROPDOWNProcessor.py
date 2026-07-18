import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class SELECT_TREE_DROPDOWNProcessor(Processor):
    TPL: str = '{"selections":"level1>level2>last level", "select_last":"yes|no", "check_from_level":1, "container_xpath":"//smq-browse-lists", "entry_class":"browse-entry", "pane_tag":"browse-pane", "text_class":"wrapped-text-content", "expand_xpath":".//div[contains(@class,\'expansion-btn\')]", "icon_xpath":".//span[contains(@class,\'display-icon\')]//md-icon", "checkbox_xpath":".//span[contains(@class,\'display-icon\')]", "checked_state":"check_box", "wait":1, "timeout":10, "skip_timeout_error":"yes|no", "chrome_name":"chrome"}'
    DESC: str = '''
        Drive a SAP Ariba cascading tree dropdown (smq-browse-lists / browse-pane / browse-entry).
        Given an ordered list of option texts (1..4 levels), it expands each level by clicking the
        entry's ">" arrow (expansion-btn) and checks the final level's checkbox. Option text is matched
        FUZZILY (contains), so a partial keyword is enough; located by visible text (.wrapped-text-content),
        scoped to the tree container.

        - selections: ">"-separated level texts, outer level first, e.g. "支持和服务>海外>亚太>迪拜院". 1 to 4 levels. Each level is matched fuzzily (partial keyword ok). Supports expression, e.g. "{level1}>{level2}" or a whole "{path}". (A list is also accepted for backward compatibility.) (required)
        - select_last: "yes" clicks the LAST level's checkbox to select it; "no" only expands it (default: "yes|no")
        - check_from_level: 1-based level from which entries get their checkbox checked; levels before it are only expanded, not checked. e.g. with "All>油气新能源>科研业务>迪拜院", 1 checks all (incl. All), 2 leaves All unchecked and checks the rest (default: 1)
        - container_xpath: xpath of the tree widget root; all lookups are scoped under it (default: "//smq-browse-lists")
        - entry_class: CSS class marking each option node (default: "browse-entry")
        - pane_tag: tag/selector of each level column, used for pane-scoped disambiguation (default: "browse-pane")
        - text_class: CSS class of the element carrying an option's visible text (default: "wrapped-text-content")
        - expand_xpath: xpath (relative to an entry) of the element to click to expand the next level (default: ".//div[contains(@class,'expansion-btn')]")
        - icon_xpath: xpath (relative to an entry) of the checkbox icon; its text equals checked_state when selected (default: ".//span[contains(@class,'display-icon')]//md-icon")
        - checkbox_xpath: fallback xpath (relative to an entry) to click for selecting (default: ".//span[contains(@class,'display-icon')]")
        - checked_state: icon text value that means "checked" (default: "check_box")
        - wait: seconds to sleep before starting, lets the widget finish rendering (default: 1)
        - timeout: max seconds to wait for each level's entry / next pane to appear (default: 10)
        - skip_timeout_error: "yes" logs & returns silently when a level's text is not found or a click is intercepted; "no" raises (default: "yes|no")
        - chrome_name: key in data_chain holding the Chrome driver (default: "chrome")
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    @staticmethod
    def _xpath_literal(s: str) -> str:
        """Embed an arbitrary string as an XPath string literal (quote/CJK safe)."""
        if "'" not in s:
            return "'" + s + "'"
        if '"' not in s:
            return '"' + s + '"'
        parts = s.split("'")
        return "concat(" + ", \"'\", ".join("'" + p + "'" for p in parts) + ")"

    # A-Z / a-z for XPath-1.0 case-folding via translate() (no lower-case() in XPath 1.0).
    _UP = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _LO = 'abcdefghijklmnopqrstuvwxyz'

    def _entry_xpath(self, container, pane_index, text):
        """Xpath for a tree entry whose visible text CONTAINS ``text``
        (fuzzy + case-insensitive).

        Fuzzy so a partial keyword is enough; case-insensitive via translate()
        so "all" matches "All" (no effect on CJK). pane_index (1-based) scopes
        the lookup to that pane; None = search the whole container. All the
        DOM-specific class/tag names come from self._cfg (see process()).
        """
        c = self._cfg
        lit = self._xpath_literal(text.lower())
        fold = "translate(normalize-space(),'%s','%s')" % (self._UP, self._LO)
        entry_pred = (
            "div[contains(concat(' ',normalize-space(@class),' '),' %s ')]"
            "[.//div[contains(@class,'%s') and contains(%s,%s)]]"
            % (c['entry_class'], c['text_class'], fold, lit)
        )
        if pane_index is not None:
            return "(%s//%s)[%d]//%s" % (container, c['pane_tag'], pane_index, entry_pred)
        return "%s//%s" % (container, entry_pred)

    def _find_entry(self, chrome, container, i, text, timeout):
        """Locate the level-i entry by text.

        Strategy (avoids the slow ``wait_for_*`` timeout on wrong guesses):
        1. Wait (with ``timeout``) for the entry to appear ANYWHERE in the
           container — this is the reliable locator and returns as soon as the
           option renders. The pane-index assumption proved unreliable, so it is
           no longer the primary path (waiting on a wrong pane index just burns
           the whole timeout).
        2. Once known-present, do an INSTANT (no-wait) pane-scoped lookup purely
           to disambiguate same-text-across-levels; use it only if it hits,
           otherwise fall back to the global match.
        """
        globs = SeleniumUtil.get_elements(chrome, 'xpath', self._entry_xpath(container, None, text), timeout)
        if not globs:
            return None
        if len(globs) == 1:
            return globs[0]
        # Ambiguous (same text in multiple panes) — try an instant pane-scoped
        # match to pick the right level; find_elements_by_x_path does NOT wait.
        try:
            paned = SeleniumUtil.find_elements_by_x_path(chrome, self._entry_xpath(container, i + 1, text))
            if paned:
                return paned[0]
        except Exception:
            pass
        return globs[0]

    def _click_sub(self, chrome, entry, sub_xpath, skip_err, what):
        """Click a sub-element of ``entry`` (display-text to expand, or the checkbox)."""
        try:
            sub = SeleniumUtil.find_sub_element_by_x_path(entry, sub_xpath)
        except Exception as ex:
            if skip_err:
                logging.info('%s sub-element missing, skip: %s', what, type(ex).__name__)
                return False
            raise
        try:
            SeleniumUtil.move_to_ele_then_click(chrome, sub)
            return True
        except Exception as ex:
            if skip_err:
                logging.info('%s click intercepted, skip: %s', what, type(ex).__name__)
                return False
            raise

    def _checkbox_state(self, entry):
        """Return the checkbox icon text (== cfg['checked_state'] when selected)."""
        try:
            icon = SeleniumUtil.find_sub_element_by_x_path(entry, self._cfg['icon_xpath'])
            return (icon.text or icon.get_attribute('innerText') or '').strip()
        except Exception:
            return ''

    def _select_checkbox(self, chrome, container, i, text, timeout, skip_err):
        """Check the entry's checkbox.

        Only click checkbox-related elements (the checkbox icon / its wrapper),
        never the text/row — in this tree that toggles expand/collapse and would
        collapse the child pane. Stop once the icon reaches cfg['checked_state'].
        Re-locates the entry each try to avoid stale references.
        """
        c = self._cfg
        candidates = [c['icon_xpath'], c['checkbox_xpath']]
        for cand in candidates:
            entry = self._find_entry(chrome, container, i, text, timeout)
            if entry is None:
                break
            if self._checkbox_state(entry) == c['checked_state']:
                return True   # already selected
            try:
                sub = SeleniumUtil.find_sub_element_by_x_path(entry, cand)
                SeleniumUtil.move_to_ele_then_click(chrome, sub)
            except Exception as ex:
                logging.debug('checkbox candidate %s click failed: %s', cand, type(ex).__name__)
                continue
            entry = self._find_entry(chrome, container, i, text, timeout)
            if entry is not None and self._checkbox_state(entry) == c['checked_state']:
                return True
        if skip_err:
            logging.info('SELECT_TREE_DROPDOWN: could not check %r (skip_timeout_error=yes)', text)
            return False
        raise Exception('SELECT_TREE_DROPDOWN: failed to check checkbox for %r' % text)

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
        if not (1 <= len(selections) <= 4):
            raise Exception('SELECT_TREE_DROPDOWN: selections must resolve to 1..4 ">"-separated texts')

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
            'expand_xpath':   self.explain_param_or_default('expand_xpath', ".//div[contains(@class,'expansion-btn')]"),
            'icon_xpath':     self.explain_param_or_default('icon_xpath', ".//span[contains(@class,'display-icon')]//md-icon"),
            'checkbox_xpath': self.explain_param_or_default('checkbox_xpath', ".//span[contains(@class,'display-icon')]"),
            'checked_state':  self.explain_param_or_default('checked_state', 'check_box'),
        }

        super().extra_wait()

        expand_x = self._cfg['expand_xpath']

        n = len(selections)
        for i, text in enumerate(selections):
            level = i + 1  # 1-based
            is_last = (i == n - 1)
            entry = self._find_entry(chrome, container, i, text, timeout)
            if entry is None:
                msg = 'SELECT_TREE_DROPDOWN: level %d text not found: %r' % (level, text)
                if skip_err:
                    logging.info('%s (skip_timeout_error=yes)', msg)
                    return
                raise Exception(msg)

            # Expand this level (unless it is the last one). The child pane is
            # rendered when the NEXT level's option is visible — that, not the
            # "opened" class, is the reliable signal. So: if the next level is
            # already present, skip the expand click entirely (avoids clicking a
            # hidden/already-open arrow); otherwise click the ">" arrow and wait
            # for the next level to render. Checking is done AFTER, since a check
            # can toggle/collapse state.
            if not is_last:
                nxt = self._entry_xpath(container, None, selections[i + 1])
                already_rendered = bool(SeleniumUtil.find_elements_by_x_path(chrome, nxt))
                if not already_rendered:
                    self._click_sub(chrome, entry, expand_x, skip_err, 'expand')
                    SeleniumUtil.wait_for_element_xpath_visible(chrome, nxt, timeout)

            # Check the checkbox when this level is at/after check_from_level.
            # The last level additionally respects select_last (no => don't check).
            should_check = level >= check_from and (select_last or not is_last)
            if should_check:
                self._select_checkbox(chrome, container, i, text, timeout, skip_err)
