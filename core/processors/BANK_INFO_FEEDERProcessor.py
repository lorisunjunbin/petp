import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class BANK_INFO_FEEDERProcessor(Processor):
    TPL: str = '{"value":"中国;ICBC;400059399234u2;32341", "country_label":"国家/地区", "bank_key_label":"银行账户信息 银行代码/ABA 传送号码", "account_label":"银行账户信息 帐号", "iban_label":"银行账户信息 IBAN 编号", "option_class":"mat-option", "wait":1, "timeout":10, "skip_timeout_error":"yes|no", "skip_if_fn":"return False", "chrome_name":"chrome"}'
    DESC: str = '''
        Fill a SAP Ariba bank-account form from one ";"-separated string with the four required fields
        in order: 国家;银行代码;账号;IBAN编号 (e.g. "中国;ICBC;400059399234u2;32341"). The 国家/地区
        field is a type-ahead (md-autocomplete): the country is typed, then the option whose visible
        text EXACTLY equals the country is clicked from the popup (typing "中国" also lists "中立区"/
        "中非共和国", so exact match matters). The other three are plain text inputs (clear + type),
        located by their aria-label.

        - value: ";"-separated "国家;银行代码;账号;IBAN" — all four required (supports expression, e.g. "{bank_info}") (required)
        - country_label: aria-label of the country type-ahead input (default: "国家/地区")
        - bank_key_label: aria-label of the bank-code input (default: "银行账户信息 银行代码/ABA 传送号码")
        - account_label: aria-label of the account-number input (default: "银行账户信息 帐号")
        - iban_label: aria-label of the IBAN input (default: "银行账户信息 IBAN 编号")
        - option_class: CSS class of each autocomplete option row (default: "mat-option")
        - wait: seconds to sleep before starting (default: 1)
        - timeout: max seconds to wait for an input / the option list to appear (default: 10)
        - skip_timeout_error: "yes" logs & continues when an input/option is not found; "no" raises (default: "yes|no")
        - skip_if_fn: Python function body receiving (p); return True to SKIP this whole processor before locating anything (default: "return False")
        - chrome_name: key in data_chain holding the Chrome driver (default: "chrome")
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):
        super().process()
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')

        raw = self.expression2str(str(self.get_param('value')))
        parts = [p.strip() for p in raw.split(';')]
        if len(parts) < 4 or not all(parts[:4]):
            raise Exception('BANK_INFO_FEEDER: value must be "国家;银行代码;账号;IBAN" — all four required, got %r' % raw)
        country, bank_key, account, iban = parts[0], parts[1], parts[2], parts[3]

        country_label = self.explain_param_or_default('country_label', '国家/地区')
        bank_key_label = self.explain_param_or_default('bank_key_label', '银行账户信息 银行代码/ABA 传送号码')
        account_label = self.explain_param_or_default('account_label', '银行账户信息 帐号')
        iban_label = self.explain_param_or_default('iban_label', '银行账户信息 IBAN 编号')
        option_class = self.explain_param_or_default('option_class', 'mat-option')
        timeout = int(self.get_param('timeout')) if self.has_param('timeout') else 10
        skip_err = self.get_param_bool_if_equal('skip_timeout_error', 'yes')

        super().extra_wait()

        # 1) country type-ahead: type, then click the option whose text EXACTLY equals country.
        if not SeleniumUtil.select_type_ahead(chrome, country_label, option_class, country, timeout):
            return self.fail_or_skip('country %r not selected' % country, skip_err)

        # 2..4) plain text inputs: clear + type.
        for label, val, name in ((bank_key_label, bank_key, 'bank_key'),
                                  (account_label, account, 'account'),
                                  (iban_label, iban, 'IBAN')):
            if not SeleniumUtil.fill_input_by_label(chrome, label, val, timeout):
                return self.fail_or_skip('%s input %r not found' % (name, label), skip_err)

        logging.info('BANK_INFO_FEEDER: filled country=%r bank_key=%r account=%r iban=%r',
                     country, bank_key, account, iban)
