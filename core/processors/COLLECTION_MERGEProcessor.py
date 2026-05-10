import logging

from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil


class COLLECTION_MERGEProcessor(Processor):
    TPL: str = '{"c_one_name":"","c_two_name":"","c_result_name":"", "lambda_finder":"rowc1[0] == rowc2[0]", "lambda_merge_matched":"rowc1 + rowc2"}'

    DESC: str = '''
        Find matched rows from two collections and merge them into a result collection.

        - c_one_name: key of data_chain pointing to the first collection
        - c_two_name: key of data_chain pointing to the second collection
        - c_result_name: key of data_chain to store the merged result
        - lambda_finder: Python expression to match rows, variables "rowc1" and "rowc2" are available (default: "rowc1[0] == rowc2[0]")
        - lambda_merge_matched: Python expression to merge matched rows, variables "rowc1" and "rowc2" are available (default: "rowc1 + rowc2")
    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        c_one_name = self.get_param('c_one_name')
        c_one = self.get_data(c_one_name)
        logging.debug(f'The size of "{c_one_name}": {len(c_one)}')

        c_two_name = self.get_param('c_two_name')
        c_two = self.get_data(c_two_name)
        logging.debug(f'The size of "{c_two_name}": {len(c_two)}')

        lambda_finder = self.get_param('lambda_finder')
        lambda_finder_func = CodeExplainerUtil.create_and_execute_func('COLLECTION_MERGEProcessor_finder', '(rowc1, rowc2, p)',
                                                            'return ' + lambda_finder)

        lambda_merge = self.get_param('lambda_merge_matched')
        lambda_merge_func = CodeExplainerUtil.create_and_execute_func('COLLECTION_MERGEProcessor_merge', '(rowc1, rowc2, p)',
                                                           'return ' + lambda_merge)
        c_result = []

        for idxc1, rowc1 in enumerate(c_one):
            for idxc2, rowc2 in enumerate(c_two):
                if lambda_finder_func(rowc1, rowc2, self):
                    merged_row = lambda_merge_func(rowc1, rowc2, self)
                    c_result.append(merged_row)
                    # logging.debug(f'Found matched row then merge [{idxc1}:{idxc2}] -> {str(merged_row)}')

        c_result_name = self.get_param('c_result_name')
        logging.debug(f'The size of "{c_result_name}" after merged: {len(c_result)}')

        self.populate_data(c_result_name, c_result)
