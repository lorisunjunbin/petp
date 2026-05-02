import logging
from core.processor import Processor


class DATA_MAPPINGProcessor(Processor):
    TPL: str = '{"source_key":"", "map_fn":"[item.id, item.title]", "start_idx":"","end_idx":"", "target_key":""}'

    DESC: str = '''
        Map/transform each element in source_key using map_fn expression and store result in target_key.
        Supports slicing via start_idx/end_idx. Replace source_key if target_key is not given.

        - source_key: key of data_chain pointing to the source list
        - map_fn: Python expression to transform each element, variable "item" is available (default: "[item.id, item.title]")
        - start_idx: start index for slicing the collection (optional, supports expression)
        - end_idx: end index for slicing the collection, inclusive (optional, supports expression)
        - target_key: key of data_chain to store the mapped result (optional, defaults to source_key)
    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        given_collection_name = self.get_param('source_key')
        given_collection = self.get_data(given_collection_name)

        logging.info('Mapping collection "%s": %d items', given_collection_name, len(given_collection))
        logging.debug('source_key: %s', given_collection)

        # --- optional slice: start_idx / end_idx ---
        start_idx_raw = self.explain_param_or_default('start_idx', '')
        end_idx_raw = self.explain_param_or_default('end_idx', '')

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

            logging.debug('Slicing "%s" from index %s to %s (inclusive).', given_collection_name, start_idx, end_idx)
            given_collection = given_collection[start_idx: end_idx + 1]
            logging.debug(f'After slicing given_collection: {given_collection}.')
        # --- end slice ---

        lambda_expression = lambda item: eval(self.get_param('map_fn'))

        target_collection_name = self.get_param('target_key') if self.has_param('target_key') \
            else given_collection_name

        target_collection = list(map(lambda_expression, given_collection))
        logging.debug(f'The size of "{target_collection_name}" after mapping: {len(target_collection)}')
        logging.debug(f'"{target_collection_name}" : {str(target_collection)}')

        self.populate_data(target_collection_name, target_collection)
