import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class CONTACT_FEEDERProcessor(Processor):
    TPL: str = '{"value":"街道;地区;邮编;城市;国家;省;电话;邮箱", "option_class":"mat-option", "wait":1, "timeout":10, "skip_timeout_error":"yes|no", "skip_if_fn":"return False", "chrome_name":"chrome"}'
    DESC: str = '''
        Fill a SAP Ariba office-address contact block from one ";"-separated string with eight fields
        in order: 街道;地区;邮编;城市;国家;省;电话;邮箱 (any field may be blank to skip it). Six are plain
        text inputs located by aria-label (街道 / 地区 / 邮政编码 / 城市 / 电话 / 电子邮箱, cleared then
        typed). 国家/地区 and 州/省/地区 are BOTH type-aheads (md-autocomplete): the value is typed, then
        the option whose visible text EXACTLY equals it is clicked — or, if none, the unique option that
        CONTAINS it (so a province typed as "辽宁" matches the listed "辽宁(070)", and "中国" is picked
        exactly rather than "中立区"/"中非共和国").

        - value: ";"-separated 街道;地区;邮编;城市;国家;省;电话;邮箱 — eight positions, blank = skip that field (supports expression, e.g. "{contact}") (required)
        - option_class: CSS class of each autocomplete option row (default: "mat-option")
        - wait: seconds to sleep before starting (default: 1)
        - timeout: max seconds to wait for an input / the option list to appear (default: 10)
        - skip_timeout_error: "yes" logs & continues when an input/option is not found; "no" raises (default: "yes|no")
        - skip_if_fn: Python function body receiving (p); return True to SKIP this whole processor before locating anything (default: "return False")
        - chrome_name: key in data_chain holding the Chrome driver (default: "chrome")
    '''

    # Positional field -> (display name, input aria-label, is_type_ahead).
    # 国家/地区 and 州/省/地区 are BOTH type-ahead (md-autocomplete): type, then
    # click the option whose text exactly equals the value.
    _FIELDS = [
        ('街道', '街道', False),
        ('地区', '地区', False),
        ('邮编', '邮政编码', False),
        ('城市', '城市', False),
        ('国家', '国家/地区', True),
        ('省', '州/省/地区', True),
        ('电话', '电话', False),
        ('邮箱', '电子邮箱', False),
    ]

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):
        super().process()
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')

        raw = self.expression2str(str(self.get_param('value')))
        parts = [p.strip() for p in raw.split(';')]
        # pad so a short string just leaves later fields blank
        parts += [''] * (len(self._FIELDS) - len(parts))

        option_class = self.explain_param_or_default('option_class', 'mat-option')
        timeout = int(self.get_param('timeout')) if self.has_param('timeout') else 10
        skip_err = self.get_param_bool_if_equal('skip_timeout_error', 'yes')

        super().extra_wait()

        filled = []
        for (name, aria_label, is_type_ahead), val in zip(self._FIELDS, parts):
            if not val:
                continue   # blank position -> skip this field
            if is_type_ahead:
                ok = SeleniumUtil.select_type_ahead(chrome, aria_label, option_class, val, timeout)
            else:
                ok = SeleniumUtil.fill_input_by_label(chrome, aria_label, val, timeout)
            if not ok:
                return self.fail_or_skip('%s (%s) not filled with %r' % (name, aria_label, val), skip_err)
            filled.append('%s=%r' % (name, val))
        logging.info('CONTACT_FEEDER: filled %s', ', '.join(filled) if filled else '(nothing)')
