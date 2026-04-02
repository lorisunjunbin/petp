import logging
from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil


class DATA_CONVERTProcessor(Processor):
    TPL: str = '{"given_key":"", "convertor_func":"return [p.get_now_str(), given]", "target_key":""}'

    DESC: str = f'''
        Retrieve a value from the data_chain by key, transform it using a custom Python
        function string, and store the result back into the data_chain under a target key.

        The convertor_func has access to two variables:
          - p: the current processor instance (e.g. p.get_now_str())
          - given: the value retrieved from given_key

        - given_key: Key in data_chain whose value will be converted (supports expression, default: "")
        - convertor_func: Python function body that takes (p, given) and returns the converted value (supports expression, default: "return [p.get_now_str(), given]")
        - target_key: Key in data_chain to store the converted result (supports expression, default: "")

        {TPL}

    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        given = self.get_data(self.get_param('given_key'))
        convertor_func_body = self.expression2str(self.get_param('convertor_func'))
        target_key = self.get_param('target_key')

        convertor_func = CodeExplainerUtil.create_and_execute_func('DATA_CONVERTProcessor_convertor', '(p, given)',
                                                                   convertor_func_body)
        target_value = convertor_func(self, given)

        logging.debug(f'"{target_key}" after collecting: {str(target_value)}')

        self.populate_data(target_key, target_value)

