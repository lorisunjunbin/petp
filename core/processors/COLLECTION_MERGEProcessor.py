import logging

from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil


class COLLECTION_MERGEProcessor(Processor):
    TPL: str = '{"c_one_name":"","c_two_name":"","c_result_name":"", "lambda_finder":"rowc1[0] == rowc2[0]", "lambda_merge_matched":"rowc1 + rowc2"}'

    DESC: str = f''' 
        Find matched rows from c_one and c_two, merge them into c_result, find by lambda_finder, merge by lambda_merge_matched.
        {TPL}
    '''

    def process(self):
        c_one_name = self.get_param('c_one_name')
        c_one = self.get_data(c_one_name)
        logging.debug(f'The size of "{c_one_name}": {len(c_one)}')

        c_two_name = self.get_param('c_two_name')
        c_two = self.get_data(c_two_name)
        logging.debug(f'The size of "{c_two_name}": {len(c_two)}')

        lambda_finder = self.get_param('lambda_finder')
        lambda_finder_func = CodeExplainerUtil.func_wrapper('COLLECTION_MERGEProcessor_finder', '(rowc1, rowc2)',
                                                            'return ' + lambda_finder)

        lambda_merge = self.get_param('lambda_merge_matched')
        lambda_merge_func = CodeExplainerUtil.func_wrapper('COLLECTION_MERGEProcessor_merge', '(rowc1, rowc2)',
                                                           'return ' + lambda_merge)
        c_result = []

        for idxc1, rowc1 in enumerate(c_one):
            for idxc2, rowc2 in enumerate(c_two):
                if lambda_finder_func(rowc1, rowc2):
                    merged_row = lambda_merge_func(rowc1, rowc2)
                    c_result.append(merged_row)
                    # logging.debug(f'Found matched row then merge [{idxc1}:{idxc2}] -> {str(merged_row)}')

        c_result_name = self.get_param('c_result_name')
        logging.debug(f'The size of "{c_result_name}" after merged: {len(c_result)}')

        self.populate_data(c_result_name, c_result)
