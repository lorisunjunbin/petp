import logging

from core.processor import Processor
from utils.OSUtils import OSUtils
from utils.SafePaths import validate_path


class FILE_DELETEProcessor(Processor):
    TPL: str = '{"file_path":"path/to/folder/file"}'
    DESC: str = '''
        Delete the file at the given absolute file_path.

        - file_path: absolute path of the file to delete (supports expression)
    '''
    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):
        fp = validate_path(self.expression2str(self.get_param('file_path')))
        logging.info('Deleting file: %s', fp)
        OSUtils.delete_file_if_existed(fp)
