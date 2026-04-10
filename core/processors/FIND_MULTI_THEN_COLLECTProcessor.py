import logging

from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil
from utils.SeleniumUtil import SeleniumUtil


class FIND_MULTI_THEN_COLLECTProcessor(Processor):
    TPL: str = '{"collectby":"xpath|css","identity":"","value_type":"text|value|ele|_any property or attribute_", "value_key":"name_of_collecttion", "wait":5, "timeout":10, "skip_fn":"return ele is None","sort_lambda":"item", "sort_reverse":"no"}'

    DESC = f'''
        Find multiple elements via selenium and collect their text, value, or any property/attribute into a list.

        - collectby: locator type, "xpath" or "css"
        - identity: locator value for the target elements
        - value_type: what to collect - "text" for element.text, "value" for input value, "ele" for element itself, or any attribute name
        - value_key: key of data_chain to store the collected list (supports expression)
        - wait: extra wait in seconds before locating elements (default: 5)
        - timeout: max seconds to wait for elements to appear (default: 10)
        - skip_fn: Python function body to skip elements, variable "ele" is available (default: "return ele is None")
        - sort_lambda: Python expression for sorting, variable "item" is available (default: "item")
        - sort_reverse: "yes" to sort in descending order (default: "no")

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
        skip_fn_body = self.expression2str(self.get_param('skip_fn')) \
            if self.has_param('skip_fn') and len(self.get_param('skip_fn')) > 0 \
            else None
        sort_lambda = (lambda item: eval(self.expression2str(self.get_param('sort_lambda')))) if self.has_param('sort_lambda') else None
        sort_reverse = self.get_param('sort_reverse').lower() == 'yes' if self.has_param('sort_reverse') else False
        skip_fn = CodeExplainerUtil.create_and_execute_func('FIND_MULTI_THEN_COLLECTProcessor_skip_fn', '(ele)',
                                                            skip_fn_body) if skip_fn_body else None
        valueCollection = []

        super().extra_wait()
        elements = SeleniumUtil.get_elements(chrome, collectby, identity, time_out)

        for ele in elements:
            if skip_fn and skip_fn(ele):
                continue

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

        if sort_lambda is not None:
            valueCollection.sort(key=sort_lambda, reverse=sort_reverse)
            logging.info(
                f'collecting after sorting by lambda "{self.get_param("sort_lambda")}", multi "{value_key}" : {str(valueCollection)}')
        else:
            logging.info(f'collecting multi "{value_key}" : {str(valueCollection)}')

        self.populate_data(value_key, valueCollection)
