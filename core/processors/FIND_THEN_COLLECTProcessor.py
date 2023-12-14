import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class FIND_THEN_COLLECTProcessor(Processor):
    TPL: str = '{"collectby":"id|xpath|css","identity":"","value_type":"text|value|any", "value_key":"name_of_collect", "wait":1, "timeout":10}'

    DESC = f'''
    get single text/property/attribute from given element via selenium 

    {TPL}

    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):

        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')

        collectby = self.get_param('collectby')
        value_type = self.get_param('value_type')
        value_key = self.expression2str(self.get_param('value_key'))
        identity = self.get_param('identity')
        time_out = int(self.get_param('timeout')) if self.has_param('timeout') else 10

        super().extra_wait()

        ele = SeleniumUtil.get_element_by(chrome, collectby, identity, time_out)

        valueCollected = None

        if value_type == 'text' and ele is not None:
            valueCollected = ele.text

        if value_type == 'value' and ele is not None:
            valueCollected = ele.get_property('value')

        if valueCollected is None and value_type is not None and ele is not None:
            valueCollected = self.get_property_or_attribute(ele, value_type)

        logging.info(f'collecting "{value_key}" : {str(valueCollected)}')

        if self.is_in_loop:
            self.append_data_for_loop(value_key, valueCollected)
        else:
            self.populate_data(value_key, valueCollected)
