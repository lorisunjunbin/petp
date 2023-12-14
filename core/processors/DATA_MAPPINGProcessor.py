import logging
from core.processor import Processor


class DATA_MAPPINGProcessor(Processor):
    TPL: str = '{"given_collection":"", "lambda":"[item.id, item.title]", "target_collection":""}'

    DESC: str = f''' 

        convert element in given_collection associated with lambda expression and store it in target_collection.
        Replace given_collection if target_collection is not given.
        
        {TPL}

    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        given_collection_name = self.get_param('given_collection')
        given_collection = self.get_data(given_collection_name)

        lambda_expression = lambda item: eval(self.get_param('lambda'))

        target_collection_name = self.get_param('target_collection') if self.has_param('target_collection') \
            else given_collection_name

        target_collection = list(map(lambda_expression, given_collection))
        logging.debug(f'The size of "{target_collection_name}" after mapping: {len(target_collection)}')
        logging.debug(f'"{target_collection_name}" : {str(target_collection)}')

        self.populate_data(target_collection_name, target_collection)
