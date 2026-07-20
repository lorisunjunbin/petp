import logging
import time
from datetime import datetime

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class DATE_PICKERProcessor(Processor):
    TPL: str = '{"date":"2026-07-20", "date_format":"%Y-%m-%d", "open_xpath":"//button[@aria-label=\'Open calendar\']", "calendar_xpath":"//md-datepicker-content", "max_nav":24, "wait":1, "timeout":10, "skip_timeout_error":"yes|no", "skip_if_fn":"return False", "chrome_name":"chrome"}'
    DESC: str = '''
        Pick a date in an Angular Material datepicker (md-datepicker-content calendar popup).
        Given a date like "2026-07-20", it opens the calendar, navigates prev/next months to the
        target month if needed, and clicks the day cell. The day cell is matched by its English
        aria-label (e.g. "July 20, 2026") — the reliable, unique locator Material renders. Useful for
        readonly date inputs that reject send_keys and only accept picking from the calendar.

        - date: the target date (supports expression, e.g. "{reg_date}") (required)
        - date_format: strptime format of `date` (default: "%Y-%m-%d")
        - open_xpath: xpath of the button that OPENS the calendar. Empty = assume already open. (default: "//button[@aria-label='Open calendar']")
        - calendar_xpath: xpath of the calendar popup root; navigation & day lookups are scoped under it (default: "//md-datepicker-content")
        - max_nav: safety cap on how many prev/next month clicks are allowed (default: 24)
        - wait: seconds to sleep before starting (default: 1)
        - timeout: max seconds to wait for the calendar / day cell to appear (default: 10)
        - skip_timeout_error: "yes" logs & continues when the calendar/day is not found or a click fails; "no" raises (default: "yes|no")
        - skip_if_fn: Python function body receiving (p); return True to SKIP this whole processor before locating anything (e.g. when date is built from a data_chain value that may be absent). Default runs the processor. (default: "return False")
        - chrome_name: key in data_chain holding the Chrome driver (default: "chrome")
    '''

    # Fixed English month names/abbreviations — Material renders these regardless
    # of the OS locale, so we must NOT rely on strftime('%B') which is locale-dependent.
    _MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
    _MON_ABBR = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    @classmethod
    def _target_aria(cls, dt) -> str:
        """The day cell's aria-label, e.g. 'July 20, 2026'. Day has NO leading
        zero (Material renders 'July 1, 2026'), and the month name is the fixed
        English name — not strftime('%B'), which depends on the OS locale."""
        return '%s %d, %d' % (cls._MONTHS[dt.month - 1], dt.day, dt.year)

    @classmethod
    def _parse_period(cls, text):
        """Parse the period button text (e.g. 'JUL 2026') into (year, month).
        Returns None if it can't be parsed."""
        if not text:
            return None
        up = text.upper()
        year = None
        for tok in up.replace(',', ' ').split():
            if tok.isdigit() and len(tok) == 4:
                year = int(tok)
                break
        month = None
        for i, abbr in enumerate(cls._MON_ABBR):
            if abbr in up:
                month = i + 1
                break
        if year is None or month is None:
            return None
        return (year, month)

    def process(self):
        super().process()
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')

        date_str = self.expression2str(str(self.get_param('date'))).strip()
        if not date_str:
            raise Exception('DATE_PICKER: date must resolve to a non-empty value')
        date_format = self.explain_param_or_default('date_format', '%Y-%m-%d')
        try:
            dt = datetime.strptime(date_str, date_format)
        except ValueError as ex:
            raise Exception('DATE_PICKER: cannot parse date %r with format %r: %s'
                            % (date_str, date_format, ex))

        calendar_xpath = self.explain_param_or_default('calendar_xpath', '//md-datepicker-content')
        open_xpath = self.explain_optional('open_xpath', '')
        timeout = int(self.get_param('timeout')) if self.has_param('timeout') else 10
        max_nav = int(self.get_param('max_nav')) if self.has_param('max_nav') else 24
        skip_err = self.get_param_bool_if_equal('skip_timeout_error', 'yes')

        super().extra_wait()

        if not self._open(chrome, open_xpath, calendar_xpath, timeout):
            return self._fail('calendar did not open', skip_err)

        self._navigate(chrome, calendar_xpath, (dt.year, dt.month), max_nav)

        aria = self._target_aria(dt)
        if not self._click_day(chrome, calendar_xpath, aria, timeout):
            return self._fail('day cell not found/clickable: %r' % aria, skip_err)
        logging.info('DATE_PICKER: picked %s', aria)

    def _fail(self, msg, skip_err):
        full = 'DATE_PICKER: ' + msg
        if skip_err:
            logging.info('%s (skip_timeout_error=yes)', full)
            return
        raise Exception(full)

    def _open(self, chrome, open_xpath, calendar_xpath, timeout):
        """Ensure the calendar popup is open. If it's already present, do
        nothing; else click open_xpath and wait for the popup."""
        if SeleniumUtil.find_elements_by_x_path(chrome, calendar_xpath):
            return True
        if open_xpath:
            eles = SeleniumUtil.find_elements_by_x_path(chrome, open_xpath)
            if eles:
                result = SeleniumUtil.click_with_fallback(chrome, eles[0])
                logging.info('DATE_PICKER: open via %r -> %s', open_xpath, result)
        # Poll for the calendar popup to render.
        deadline = time.time() + max(1, timeout)
        while time.time() < deadline:
            if SeleniumUtil.find_elements_by_x_path(chrome, calendar_xpath):
                return True
            time.sleep(0.3)
        return False

    def _current_period(self, chrome, calendar_xpath):
        eles = SeleniumUtil.find_elements_by_x_path(
            chrome, calendar_xpath + "//button[contains(@class,'mat-calendar-period-button')]")
        if not eles:
            return None
        try:
            return self._parse_period((eles[0].text or '').strip())
        except Exception:
            return None

    def _navigate(self, chrome, calendar_xpath, target_ym, max_nav):
        """Navigate to the target month via the YEAR view (fast, works across
        many years):
          1) open the year view by clicking the period button (e.g. 'JUL 2026'),
             where prev/next step by ±1 YEAR (not month);
          2) click prev/next until the shown year equals the target year;
          3) click the target month cell (aria-label like 'September 2027'),
             which returns to that month's day view.
        Falls back to doing nothing gracefully if the calendar isn't in the
        expected state. max_nav caps the year steps.
        """
        target_year, target_month = target_ym
        cur = self._current_period(chrome, calendar_xpath)
        if cur is None:
            logging.info('DATE_PICKER: cannot read current month; skip navigation')
            return
        if cur == target_ym:
            return

        # 1) open year view
        period_btn = calendar_xpath + "//button[contains(@class,'mat-calendar-period-button')]"
        eles = SeleniumUtil.find_elements_by_x_path(chrome, period_btn)
        if not eles:
            logging.info('DATE_PICKER: period button missing; stop at %r', cur)
            return
        SeleniumUtil.click_with_fallback(chrome, eles[0])
        time.sleep(0.2)

        # 2) step the year with prev/next (now ±1 year in year view)
        prev_btn = calendar_xpath + "//button[contains(@class,'mat-calendar-previous-button')]"
        next_btn = calendar_xpath + "//button[contains(@class,'mat-calendar-next-button')]"
        cur_year = self._current_year(chrome, calendar_xpath)
        for _ in range(max(0, max_nav)):
            if cur_year is None:
                logging.info('DATE_PICKER: cannot read year in year view; stop')
                return
            if cur_year == target_year:
                break
            btn_xpath = next_btn if target_year > cur_year else prev_btn
            btns = SeleniumUtil.find_elements_by_x_path(chrome, btn_xpath)
            if not btns:
                logging.info('DATE_PICKER: year nav button missing; stop at %d', cur_year)
                return
            SeleniumUtil.click_with_fallback(chrome, btns[0])
            time.sleep(0.2)
            after = self._current_year(chrome, calendar_xpath)
            if after == cur_year:     # click didn't change the year — boundary/no-op
                logging.info('DATE_PICKER: year did not change from %d; stop', cur_year)
                return
            cur_year = after
        else:
            logging.info('DATE_PICKER: reached max_nav (%d) before year %d', max_nav, target_year)
            return

        # 3) click the target month cell -> returns to that month's day view
        month_aria = '%s %d' % (self._MONTHS[target_month - 1], target_year)
        month_xp = (calendar_xpath + "//td[contains(concat(' ',normalize-space(@class),' '),"
                    " ' mat-calendar-body-cell ') and @aria-label=%s]" % SeleniumUtil.xpath_literal(month_aria))
        mcells = SeleniumUtil.find_elements_by_x_path(chrome, month_xp)
        if not mcells:
            logging.info('DATE_PICKER: month cell %r not found in year view', month_aria)
            return
        SeleniumUtil.click_with_fallback(chrome, mcells[0])
        time.sleep(0.2)

    def _current_year(self, chrome, calendar_xpath):
        """Read the year shown in the year view: the period button still shows
        the year (e.g. '2027'), so parse the first 4-digit run from its text."""
        eles = SeleniumUtil.find_elements_by_x_path(
            chrome, calendar_xpath + "//button[contains(@class,'mat-calendar-period-button')]")
        if not eles:
            return None
        text = (eles[0].text or '').upper()
        for tok in text.replace(',', ' ').split():
            if tok.isdigit() and len(tok) == 4:
                return int(tok)
        return None

    def _click_day(self, chrome, calendar_xpath, aria, timeout):
        xp = (calendar_xpath + "//td[contains(concat(' ',normalize-space(@class),' '),"
              " ' mat-calendar-body-cell ') and @aria-label=%s]" % SeleniumUtil.xpath_literal(aria))
        eles = SeleniumUtil.get_elements(chrome, 'xpath', xp, timeout)
        if not eles:
            return False
        result = SeleniumUtil.click_with_fallback(chrome, eles[0])
        logging.info('DATE_PICKER: click day %r -> %s', aria, result)
        return result in ('native', 'move')
