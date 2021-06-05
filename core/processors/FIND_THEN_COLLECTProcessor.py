from core.processor import Processor


class FIND_THEN_COLLECTProcessor(Processor):
    TPL: str = '{"collectby":"id|xpath|css","identity":"","value_type":"text|value|any", "value_key":"name_of_collect"}'

    def process(self):

        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')

        collectby = self.get_param('collectby')
        value_type = self.get_param('value_type')
        value_key = self.get_param('value_key')
        identity = self.get_param('identity')
        ele = self.get_element_by(chrome, collectby, identity)

        valueCollected = ''

        if value_type == 'text':
            valueCollected = ele.text

        if value_type == 'value':
            valueCollected = ele.get_property('value')

        if value_type == 'any':
            valueCollected = self.getValue(ele)

        self.populate_data(value_key, valueCollected)

    def getValue(self, ele):
        try:
            return ele.text
        except:
            return ele.get_attribute('value')
