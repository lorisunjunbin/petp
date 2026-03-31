from core.processor import Processor

class INITIAL_PARAMSProcessor(Processor):
    TPL: str = '{"any_key":"any_value"}'

    DESC: str = f''' 
        - Initial key-value pairs, save to data_chain, can be used in f-string via: self.get_data("any_key"), any_value support expression2str.

        {TPL}

    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        allParams = self.get_all_params()
        for key in allParams:
            value = allParams[key]
            self.populate_data(key, self.expression2str(value) if value is not None else None)
