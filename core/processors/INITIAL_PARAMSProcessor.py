from core.processor import Processor

class INITIAL_PARAMSProcessor(Processor):
    TPL: str = '{"any_key":"any_value"}'

    DESC: str = f'''
        Initialize key-value pairs and save to data_chain. All parameters are treated as key-value pairs.
        Values support expression2str for dynamic evaluation.

        - any_key: any_value - arbitrary key-value pairs to initialize in data_chain

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        allParams = self.get_all_params()
        for key in allParams:
            value = allParams[key]
            self.populate_data(key, self.expression2str(value) if value is not None else None)
