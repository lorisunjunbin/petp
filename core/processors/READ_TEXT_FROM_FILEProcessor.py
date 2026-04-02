from core.processor import Processor


class READ_TEXT_FROM_FILEProcessor(Processor):
    TPL: str = '{"file_path":"","data_key":""}'
    DESC: str = f'''
        Read the entire content of a text file and store it in data_chain under the specified key.

        - file_path: path to the text file to read from (supports expression, default: "")
        - data_key: key in data_chain to store the file content as a string (supports expression, default: "")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):
        file_path = self.expression2str(self.get_param('file_path'))
        data_key = self.expression2str(self.get_param('data_key'))

        with open(file_path, "r+", encoding='utf8') as text_file:
            self.populate_data(data_key, text_file.read())
