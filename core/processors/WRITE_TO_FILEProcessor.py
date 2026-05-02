import logging

from core.processor import Processor


class WRITE_TO_FILEProcessor(Processor):
    TPL: str = '{"file_path":"", "content":"", "data_key":""}'
    DESC: str = '''
        Write string content to a file on disk using UTF-8 encoding.
        On success, the file path is saved to the data_chain under the specified key.

        - file_path: Absolute or relative path of the file to write (supports expression, default: "")
        - content: String content to write into the file (supports expression, default: "")
        - data_key: Key name in data_chain to store the written file path; if empty, no data is stored (supports expression, default: "")
    '''
    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):
        file_path = self.expression2str(self.get_param('file_path'))
        content = self.expression2str(self.get_param('content'))

        with open(file_path, "w", encoding='utf8') as text_file:
            text_file.write(content)

        logging.info('Written to file: %s (%d chars)', file_path, len(content))
        self.populate_data(self.get_param('data_key'), file_path)
