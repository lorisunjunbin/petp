import json
import logging

from core.processor import Processor


class NESTED_TO_FLAT_CONVERTORProcessor(Processor):
    TPL: str = '{"data":"", "data_key":"", "data_flat_key":"", "prefix":"", "separator":"."}'

    DESC: str = '''
        Convert nested dict to flat dict. Supports nested dicts and lists.

        - data: nested JSON string to convert (used when data_key is not set)
        - data_key: key of data_chain pointing to the nested dict to convert (takes priority over data)
        - data_flat_key: key of data_chain to store the flattened dict result
        - prefix: prefix for flattened keys (optional, default: "")
        - separator: separator between nested key levels (default: ".")
    '''
    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):

        data_nested = self.expression2str(self.get_param('data_key')) if self.has_param('data_key') else json.loads(self.get_param('data'))
        
        prefix = self.explain_param_or_default('prefix', '')
        separator = self.explain_param_or_default('separator', '.')
        
        data_flat = {}
        self.convertNestedToFlat(data_nested, data_flat, separator, prefix)
        logging.debug('Converted nested to flat: %d keys', len(data_flat))
        self.populate_data(self.get_param('data_flat_key'), data_flat)
        
    def convertNestedToFlat(self, nested:dict, flat:dict, separator='.', prefix=''):
        for key in nested:
            obj = nested[key]
            if type(obj) is dict:
                self.convertNestedToFlat(obj, flat, separator, f'{prefix}{key}{separator}')
            elif type(obj) is list:
                for idx, item in enumerate(obj):
                    self.convertNestedToFlat(item, flat, separator, f'{prefix}{key}[{idx}]{separator}')
            else:
                flat[f'{prefix}{key}'] = obj    
