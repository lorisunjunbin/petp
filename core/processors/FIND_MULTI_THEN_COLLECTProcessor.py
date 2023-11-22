from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class FIND_MULTI_THEN_COLLECTProcessor(Processor):
    TPL: str = '{"collectby":"xpath|css","identity":"","value_type":"text|value", "value_key":"name_of_collecttion"}'

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
        value_key = self.get_param('value_key')
        identity = self.get_param('identity')

        elements = SeleniumUtil.get_elements(chrome, collectby, identity)

        valueCollection = []

        for ele in elements:
            new_value = None
            if value_type == 'text':
                new_value = ele.text

            if value_type == 'value':
                new_value = ele.get_property('value')

            if new_value is None and value_type  is not None:
                new_value = self.get_property_or_attribute(ele, value_type)
            if new_value is not None:
                valueCollection.append(new_value)

        self.populate_data(value_key, valueCollection)

