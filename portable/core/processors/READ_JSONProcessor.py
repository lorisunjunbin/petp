import json
import logging

from jsonpath import JSONPath

from core.processor import Processor
from utils.SafePaths import validate_path


class READ_JSONProcessor(Processor):
    TPL: str = '{"file_path":"", "file_path_key":"str on data_chain", "json_path":"$.*", "data_key":"name on data_chain"}'

    DESC: str = '''
        Load JSON from file, optionally extract data via json_path, then save to data_chain.

        - file_path: JSON file path (supports expression)
        - file_path_key: key of data_chain to get the file path, takes priority over file_path if set
        - json_path: JSONPath expression to extract specific data (default: "$.*", refer to https://pypi.org/project/jsonpath-python/)
        - data_key: key of data_chain to store the parsed JSON data
    '''
    def get_category(self) -> str:
        return super().CATE_JSON

    def process(self):
        file_path = self.get_data(self.get_param('file_path_key')) if self.has_param('file_path_key') \
            else self.expression2str(self.get_param('file_path'))
        file_path = validate_path(file_path)

        json_path = self.get_param('json_path')

        with open(file_path, "rb") as file:
            fileContent = json.load(file)
            data = fileContent if json_path is None else JSONPath(json_path).parse(fileContent)
            logging.info('Read JSON: %s', file_path)
            self.populate_data(self.get_param('data_key'), data)
