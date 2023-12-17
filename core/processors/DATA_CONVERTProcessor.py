import logging
from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil


class DATA_CONVERTProcessor(Processor):
    TPL: str = '{"given_key":"", "convertor_func":"return [p.get_now_str(), given]", "target_key":""}'

    DESC: str = f''' 
        
        [given_key] of data_chain as input, convert it with [convertor_func], and store it in [target_key].
        
        :param p - is current DATA_CONVERTProcessor
        :param given - is data associated with [given_key]
        
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

    def test(self):
        return dict(filter(lambda itm: itm[0].startswith("__"), self.get_data_chain().items()))