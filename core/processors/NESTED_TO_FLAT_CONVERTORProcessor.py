import json
from core.processor import Processor


class NESTED_TO_FLAT_CONVERTORProcessor(Processor):
    TPL: str = '{"data":"", "data_key":"", "data_flat_key":"", "prefix":"", "separator":"."}'
    DESC: str = f''' 
        - convert nested dict to flat dict. 
        
       {TPL}       
       
    '''

    def process(self):

        data_nested = self.expression2str(self.get_param('data_key')) if self.has_param('data_key') else json.loads(self.get_param('data'))
        
        prefix = self.expression2str(self.get_param('prefix')) if self.has_param('prefix') else ''
        separator = self.expression2str(self.get_param('separator')) if self.has_param('separator') else '.'
        
        data_flat = {}
        self.convertNestedToFlat(data_nested, data_flat, separator, prefix)
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
