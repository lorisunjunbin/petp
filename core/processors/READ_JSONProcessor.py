import json

from jsonpath import JSONPath

from core.processor import Processor


class READ_JSONProcessor(Processor):
    TPL: str = '{"file_path":"", "file_path_key":"str on data_chain", "json_path":"$.*", "data_key":"name on data_chain"}'

    DESC: str = f''' 
        
        Load json from file, bind to data_chain. 
        support json_path refer to: https://pypi.org/project/jsonpath-python/

        {TPL}

    '''
    def get_category(self) -> str:
        return super().CATE_JSON

    def process(self):
        file_path = self.get_data(self.get_param('file_path_key')) if self.has_param('file_path_key') \
            else self.expression2str(self.get_param('file_path'))

        json_path = self.get_param('json_path')

        with open(file_path, "rb") as file:
            fileContent = json.load(file)

            data = fileContent if json_path is None else JSONPath(json_path).parse(fileContent)

            self.populate_data(self.get_param('data_key'), data)
