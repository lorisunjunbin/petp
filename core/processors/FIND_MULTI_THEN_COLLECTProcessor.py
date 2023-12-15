import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class FIND_MULTI_THEN_COLLECTProcessor(Processor):
    TPL: str = '{"collectby":"xpath|css","identity":"","value_type":"text|value|ele", "value_key":"name_of_collecttion", "wait":5, "timeout":10}'

    DESC = f'''
    get muti-text/property/attribute from given elements via selenium 

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

        elements = SeleniumUtil.get_elements(chrome, collectby, identity, time_out)

        valueCollection = []

        for ele in elements:
            new_value = None
            if value_type == 'text':
                new_value = ele.text

            if value_type == 'value':
                new_value = ele.get_property('value')

            if value_type == 'ele':
                new_value = ele

            if new_value is None and value_type is not None:
                new_value = SeleniumUtil.get_property_or_attribute(ele, value_type)
            if new_value is not None:
                valueCollection.append(new_value)

        logging.info(f'collecting multi "{value_key}" : {str(valueCollection)}')

        self.populate_data(value_key, valueCollection)
