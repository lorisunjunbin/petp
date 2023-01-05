import json

from core.processor import Processor
from jsonpath import JSONPath


class READ_JSONProcessor(Processor):
    TPL: str = '{"file_path":"", "file_path_key":"str on data_chain", "json_path":"$.*", "data_key":"name on data_chain"}'

    DESC: str = f''' 
        
        Load json from file, bind to data_chain. 
        support json_path refer to: https://pypi.org/project/jsonpath-python/

        {TPL}

    '''

    def process(self):
        file_path = self.get_data(self.get_param('file_path_key')) if self.has_param('file_path_key') \
            else self.expression2str(self.get_param('file_path'))

        json_path = self.get_param('json_path')

        with open(file_path, "rb") as file:
            data = json.load(file) if json_path is None else JSONPath(json_path).parse(json.load(file))
            self.populate_data(self.get_param('data_key'), data)
