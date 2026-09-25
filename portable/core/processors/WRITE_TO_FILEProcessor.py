import logging

from core.processor import Processor
from utils.SafePaths import validate_path


class WRITE_TO_FILEProcessor(Processor):
    TPL: str = '{"file_path":"", "content":"", "mode":"w|a", "data_key":""}'
    DESC: str = '''
        Write string content to a file on disk using UTF-8 encoding.
        On success, the file path is saved to the data_chain under the specified key.

        - file_path: Absolute or relative path of the file to write (supports expression, default: "")
        - content: String content to write into the file (supports expression, default: "")
        - mode: "w" to overwrite the file, "a" to append to the end (default: "w"). Use "a" inside a loop to accumulate one line per iteration
        - data_key: Key name in data_chain to store the written file path; if empty, no data is stored (supports expression, default: "")
    '''
    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):
        file_path = validate_path(self.expression2str(self.get_param('file_path')))
        content = self.expression2str(self.get_param('content')) or ''
        mode = self.explain_param_or_default('mode', 'w')
        mode = 'a' if str(mode).strip().lower() == 'a' else 'w'

        with open(file_path, mode, encoding='utf8') as text_file:
            text_file.write(content)

        logging.info('Written to file: %s (mode=%s, %d chars)', file_path, mode, len(content))
        self.populate_data(self.get_param('data_key'), file_path)
