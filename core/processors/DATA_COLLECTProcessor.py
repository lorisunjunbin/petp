import logging
from core.processor import Processor


class DATA_COLLECTProcessor(Processor):
    TPL: str = '{"clean_b4_collect":"yes|no","target":"", "type":"list|dict", "list_flatten":"yes|no", "list_row_lambda":"[me.get_data(\\"\\")]", "dict_key_lambda":"[me.get_data(\\"\\")]", "dict_value_lambda":"[me.get_data(\\"\\")]"}'

    DESC: str = f'''
        Collect data into a list or dict in data_chain via lambda expressions. Supports cleaning before collect.

        - clean_b4_collect: "yes" to clear the target before collecting, "no" to append (default: "no")
        - target: key of data_chain to store the collected data (supports expression)
        - type: collection type, "list" or "dict" (default: "list")
        - list_flatten: "yes" to flatten the collected row if it's a list, "no" to keep as is (only applicable when type is "list", default: "no")
        - list_row_lambda: Python expression for list row value, variable "me" (current processor) is available (required when type is "list")
        - dict_key_lambda: Python expression for dict key, variable "me" is available (required when type is "dict")
        - dict_value_lambda: Python expression for dict value, variable "me" is available (required when type is "dict")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        target_name = self.expression2str(self.get_param('target'))
        target_type = self.get_param('type')
        clean_b4_collect = self.expression2str(self.get_param('clean_b4_collect')) if self.has_param('clean_b4_collect') else 'no'
        list_flatten = self.expression2str(self.get_param('list_flatten')) if self.has_param('list_flatten') else 'no'

        if target_type == 'list':
            if not self.has_param('list_row_lambda'):
                logging.error(f'list_row_lambda is required for type == list')
                return

            if 'yes' == clean_b4_collect or not self.has_data(target_name):
                self.populate_data(target_name, [])

            result = self.get_data(target_name)
            collect_row = lambda me: eval(self.get_param('list_row_lambda'))
            row_value = collect_row(self)
            if str(list_flatten).strip().lower() == 'yes' and isinstance(row_value, list):
                result.extend(row_value)
            else:
                result.append(row_value)
            logging.debug(f'The size of "{target_name}" after collecting: {len(result)}')

        elif target_type == 'dict':
            if not self.has_param('dict_key_lambda') or not self.has_param('dict_value_lambda'):
                logging.error(f'dict_key_lambda and dict_value_lambda are required for type == dict')
                return

            if 'yes' == clean_b4_collect or not self.has_data(target_name):
                self.populate_data(target_name, {})

            result = self.get_data(target_name)
            collect_dict_key = lambda me: eval(self.get_param('dict_key_lambda'))
            collect_dict_value = lambda me: eval(self.get_param('dict_value_lambda'))
            result[collect_dict_key(self)] = collect_dict_value(self)
            logging.debug(f'The size of "{target_name}" after collecting: {len(result)}')
