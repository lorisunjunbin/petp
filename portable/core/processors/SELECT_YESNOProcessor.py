import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class SELECT_YESNOProcessor(Processor):
    TPL: str = '{"label":"是否民企", "value":"是|否", "group_tag":"md-radio-group", "button_tag":"md-radio-button", "text_class":"mat-radio-label-content", "wait":1, "timeout":10, "skip_timeout_error":"yes|no", "chrome_name":"chrome"}'
    DESC: str = '''
        Select the 是 / 否 radio of a SAP Ariba yes/no radio group, located by the field label.
        The group is found by FUZZILY matching ``label`` against the radio-group's aria-label
        (contains, case-insensitive) — so several same-shape yes/no groups on the same page are
        told apart by their label. Inside that group the correct radio is picked by its VISIBLE
        text (是 / 否), NOT by the radio's own aria-label (Ariba mislabels both buttons "否") and
        NOT by dynamic ids. The click is done atomically in the browser to sidestep Angular
        Material's label/input click-target quirks.

        - label: field label to locate the radio group, matched fuzzily against its aria-label, e.g. "是否民企". Supports expression, e.g. "{field}". (required)
        - value: which option to pick — accepts 是/否, yes/no, y/n, true/false, 1/0 (case-insensitive). Supports expression, e.g. "{is_private}". (required)
        - group_tag: tag/CSS selector of the radio group element carrying the aria-label (default: "md-radio-group")
        - button_tag: tag/CSS selector of each radio button element inside the group (default: "md-radio-button")
        - text_class: CSS class of the element holding a radio's visible 是/否 text (default: "mat-radio-label-content")
        - wait: seconds to sleep before starting, lets the form finish rendering (default: 1)
        - timeout: max seconds to wait for the radio group to appear (default: 10)
        - skip_timeout_error: "yes" logs & continues when the group/option is not found; "no" raises (default: "yes|no")
        - chrome_name: key in data_chain holding the Chrome driver (default: "chrome")
    '''

    # value spellings that map to 是 / 否
    _YES = {'是', 'yes', 'y', 'true', '1'}
    _NO = {'否', 'no', 'n', 'false', '0'}

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def _normalize(self, value):
        """Map a free-form value (是/否, yes/no, true/false, 1/0) to 是 or 否."""
        v = (value or '').strip().lower()
        if v in self._YES:
            return '是'
        if v in self._NO:
            return '否'
        raise Exception('SELECT_YESNO: value %r is not a yes/no value (是/否, yes/no, true/false, 1/0)' % value)

    def _select_radio_js(self, chrome, group_tag, button_tag, text_class, label, want):
        """Find the labelled radio group and click the 是/否 radio, atomically.

        Match the group by aria-label CONTAINS label (case-insensitive), then inside
        it click the radio whose visible text (text_class) equals ``want`` (是/否).
        Clicks the inner label when present (Angular Material listens there), else the
        button. Returns 'clicked' | 'group-not-found' | 'option-not-found'.
        """
        js = r"""
        var groupTag = arguments[0], btnTag = arguments[1], textClass = arguments[2];
        var wantLabel = (arguments[3] || '').toLowerCase(), want = (arguments[4] || '').trim();
        var groups = document.querySelectorAll(groupTag);
        var group = null;
        for (var i = 0; i < groups.length; i++) {
            var al = (groups[i].getAttribute('aria-label') || '').toLowerCase();
            if (al.indexOf(wantLabel) !== -1) { group = groups[i]; break; }
        }
        if (!group) return 'group-not-found';
        var btns = group.querySelectorAll(btnTag);
        for (var j = 0; j < btns.length; j++) {
            var lc = btns[j].querySelector('.' + textClass);
            var txt = ((lc ? lc.textContent : btns[j].textContent) || '').trim();
            if (txt !== want) continue;
            btns[j].scrollIntoView({block: 'center'});
            var lbl = btns[j].querySelector('label');
            (lbl || btns[j]).click();
            return 'clicked';
        }
        return 'option-not-found';
        """
        try:
            return chrome.execute_script(js, group_tag, button_tag, text_class, label, want)
        except Exception as ex:
            logging.debug('SELECT_YESNO: _select_radio_js error: %s', ex)
            return 'error'

    def process(self):
        super().process()
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')

        label = self.expression2str(str(self.get_param('label'))).strip()
        if not label:
            raise Exception('SELECT_YESNO: label is required')
        want = self._normalize(self.expression2str(str(self.get_param('value'))))

        group_tag = self.explain_param_or_default('group_tag', 'md-radio-group')
        button_tag = self.explain_param_or_default('button_tag', 'md-radio-button')
        text_class = self.explain_param_or_default('text_class', 'mat-radio-label-content')
        timeout = int(self.get_param('timeout')) if self.has_param('timeout') else 10
        skip_err = self.get_param_bool_if_equal('skip_timeout_error', 'yes')

        super().extra_wait()

        # Wait for the labelled group to render before clicking (xpath: fuzzy aria-label match).
        group_xpath = "//%s[contains(@aria-label,%s)]" % (group_tag, SeleniumUtil.xpath_literal(label))
        SeleniumUtil.get_elements(chrome, 'xpath', group_xpath, timeout)

        result = self._select_radio_js(chrome, group_tag, button_tag, text_class, label, want)
        logging.info('SELECT_YESNO: label=%r value=%r -> %s', label, want, result)
        if result != 'clicked':
            if skip_err:
                logging.info('SELECT_YESNO: not selected (%s, skip_timeout_error=yes)', result)
                return
            raise Exception('SELECT_YESNO: failed to select %r for label %r (%s)' % (want, label, result))
