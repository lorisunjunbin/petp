import logging
from core.processor import Processor


class DATA_FILTERProcessor(Processor):
    TPL: str = '{"given_collection":"", "lambda":"len(row) > 0 and len(row[0]) > 0", "filtered_collection":""}'

    DESC: str = f''' 

        Filter given_collection associated with lambda expression and store it in filtered_collection.
        Replace given_collection if filtered_collection is not given.
        
        {TPL}

    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        given_collection_name = self.get_param('given_collection')
        given_collection = self.get_data(given_collection_name)
        logging.debug(f'The size of "{given_collection_name}" before filtering: {len(given_collection)}')

        lambda_expression = lambda row: eval(self.get_param('lambda'))

        filtered_collection_name = self.get_param('filtered_collection') if self.has_param('filtered_collection') \
            else given_collection_name

        filtered_collection = list(filter(lambda_expression, given_collection))
        logging.debug(f'The size of "{filtered_collection_name}" after filtering: {len(filtered_collection)}')

        self.populate_data(filtered_collection_name, filtered_collection)
