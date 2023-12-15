import logging
from core.processor import Processor


class DATA_COLLECTProcessor(Processor):
    TPL: str = '{"target":"", "type":"list|dict", "list_row_lambda":"[me.get_data(\\"\\")]", "dict_key_lambda":"[me.get_data(\\"\\")]", "dict_value_lambda":"[me.get_data(\\"\\")]"}'

    DESC: str = f''' 
        
        based on [type], then collect data via xxx_lambda, then store into target list or dict.
        type == list, list_row_lambda is required.
        type == dict, dict_key_lambda and dict_value_lambda are required.
        
        {TPL}

    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        target_name = self.get_param('target')
        target_type = self.get_param('type')

        if target_type == 'list':
            if not self.has_param('list_row_lambda'):
                logging.error(f'list_row_lambda is required for type == list')
                return

            if not self.has_data(target_name):
                self.populate_data(target_name, [])

            result = self.get_data(target_name)
            collect_row = lambda me: eval(self.get_param('list_row_lambda'))
            result.append(collect_row(self))
            logging.debug(f'The size of "{target_name}" after collecting: {len(result)}')

        elif target_type == 'dict':
            if not self.has_param('dict_key_lambda') or not self.has_param('dict_value_lambda'):
                logging.error(f'dict_key_lambda and dict_value_lambda are required for type == dict')
                return

            if not self.has_data(target_name):
                self.populate_data(target_name, {})

            result = self.get_data(target_name)
            collect_dict_key = lambda me: eval(self.get_param('dict_key_lambda'))
            collect_dict_value = lambda me: eval(self.get_param('dict_value_lambda'))
            result[collect_dict_key(self)] = collect_dict_value(self)
            logging.debug(f'The size of "{target_name}" after collecting: {len(result)}')
