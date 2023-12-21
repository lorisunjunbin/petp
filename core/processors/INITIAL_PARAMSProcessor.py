from core.processor import Processor

"""
TODO: 
    load from json,yaml files?
    able to specify chrome properties, etc.
    
"""


class INITIAL_PARAMSProcessor(Processor):
    TPL: str = '{ "key":"value" }'
    DESC: str = f''' 
        - Initial key-value pairs, save to data_chain  

        {TPL}

    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        allParams = self.get_all_params()
        for key in allParams:
            value = allParams[key]
            self.populate_data(key, self.expression2str(value) if value is not None else None)
