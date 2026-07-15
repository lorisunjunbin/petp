import logging
from core.processor import Processor


class DATA_FILTERProcessor(Processor):
    TPL: str = '{"source_key":"", "filter_fn":"len(row) > 0 and len(row[0]) > 0", "target_key":""}'

    DESC: str = '''
        Filter source_key with filter_fn expression and store result in target_key.
        Replace source_key if target_key is not given.

        - source_key: key of data_chain pointing to the list to filter
        - filter_fn: Python lambda expression as string, variable "row" represents each element (default: "len(row) > 0 and len(row[0]) > 0")
        - target_key: key of data_chain to store the filtered result (optional, defaults to source_key)
    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        given_collection_name = self.get_param('source_key')
        given_collection = self.get_data(given_collection_name)
        logging.info(f'The size of "{given_collection_name}" before filtering: {len(given_collection)}')

        lambda_expression = lambda row: eval(self.get_param('filter_fn'))

        filtered_collection_name = self.get_param('target_key') if self.has_param('target_key') \
            else given_collection_name

        filtered_collection = list(filter(lambda_expression, given_collection))
        logging.info(f'The size of "{filtered_collection_name}" after filtering: {len(filtered_collection)}')

        self.populate_data(filtered_collection_name, filtered_collection)
