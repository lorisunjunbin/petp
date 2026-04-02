import logging
from core.processor import Processor


class DATA_MAPPINGProcessor(Processor):
    TPL: str = '{"given_collection":"", "lambda":"[item.id, item.title]", "start_idx":"","end_idx":"", "target_collection":""}'

    DESC: str = f'''
        Map/transform each element in given_collection using lambda expression and store result in target_collection.
        Supports slicing via start_idx/end_idx. Replace given_collection if target_collection is not given.

        - given_collection: key of data_chain pointing to the source list
        - lambda: Python expression to transform each element, variable "item" is available (default: "[item.id, item.title]")
        - start_idx: start index for slicing the collection (optional, supports expression)
        - end_idx: end index for slicing the collection, inclusive (optional, supports expression)
        - target_collection: key of data_chain to store the mapped result (optional, defaults to given_collection)

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        given_collection_name = self.get_param('given_collection')
        given_collection = self.get_data(given_collection_name)

        logging.info(f'given_collection: {len(given_collection)} -> {given_collection}')

        # --- optional slice: start_idx / end_idx ---
        start_idx_raw = self.expression2str(self.get_param('start_idx')) if self.has_param('start_idx') else ''
        end_idx_raw = self.expression2str(self.get_param('end_idx')) if self.has_param('end_idx') else ''

        if start_idx_raw != '' or end_idx_raw != '':
            # start_idx defaults to the first index (0) when not set
            if start_idx_raw == '':
                start_idx = 0
                logging.debug(f'start_idx not set, defaulting to first index: 0.')
            else:
                try:
                    start_idx = int(start_idx_raw)
                except ValueError:
                    raise ValueError(f'start_idx must be an integer, got: "{start_idx_raw}"')

            # end_idx defaults to the last index of the collection when not set
            if end_idx_raw == '':
                end_idx = len(given_collection) - 1
                logging.debug(f'end_idx not set, defaulting to last index: {end_idx}.')
            else:
                try:
                    end_idx = int(end_idx_raw)
                except ValueError:
                    raise ValueError(f'end_idx must be an integer, got: "{end_idx_raw}"')

            # validate range
            if start_idx > end_idx:
                raise ValueError(f'start_idx ({start_idx}) must be <= end_idx ({end_idx}).')

            logging.info(f'Slicing "{given_collection_name}" from index {start_idx} to {end_idx} (inclusive).')
            given_collection = given_collection[start_idx: end_idx + 1]
            logging.debug(f'After slicing given_collection: {given_collection}.')
        # --- end slice ---

        lambda_expression = lambda item: eval(self.get_param('lambda'))

        target_collection_name = self.get_param('target_collection') if self.has_param('target_collection') \
            else given_collection_name

        target_collection = list(map(lambda_expression, given_collection))
        logging.debug(f'The size of "{target_collection_name}" after mapping: {len(target_collection)}')
        logging.debug(f'"{target_collection_name}" : {str(target_collection)}')

        self.populate_data(target_collection_name, target_collection)
