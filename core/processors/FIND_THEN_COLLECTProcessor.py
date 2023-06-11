from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class FIND_THEN_COLLECTProcessor(Processor):
    TPL: str = '{"collectby":"id|xpath|css","identity":"","value_type":"text|value|any", "value_key":"name_of_collect"}'

    def process(self):

        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')

        collectby = self.get_param('collectby')
        value_type = self.get_param('value_type')
        value_key = self.get_param('value_key')
        identity = self.get_param('identity')
        ele = SeleniumUtil.get_element_by(chrome, collectby, identity)

        valueCollected = None

        if value_type == 'text':
            valueCollected = ele.text

        if value_type == 'value':
            valueCollected = ele.get_property('value')

        if valueCollected is None and value_type  is not None:
            valueCollected = self.get_property_or_attribute(ele, value_type)

        if self.is_in_loop:
            self.append_data_for_loop(value_key, valueCollected)
        else:
            self.populate_data(value_key, valueCollected)

