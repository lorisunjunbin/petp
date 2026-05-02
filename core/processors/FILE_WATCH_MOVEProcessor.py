import logging
import os.path

from core.processor import Processor
from utils.OSUtils import OSUtils


class FILE_WATCH_MOVEProcessor(Processor):
    TPL: str = '{"source_path":"","target_path":"", "data_key":"", "timeout":30}'
    DESC: str = '''
        Watch for a source file to appear within a timeout period, then copy it to the target location.
        The target file path is stored in data_chain under the specified key.

        - source_path: path of the source file to watch for (supports expression, default: "")
        - target_path: destination path where the file is copied to (supports expression, default: "")
        - data_key: key in data_chain to store the target file path (supports expression, default: "")
        - timeout: maximum seconds to wait for the source file to appear (default: 30)
    '''

    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):
        source_file = self.expression2str(self.get_param('source_path'))
        target_file = self.expression2str(self.get_param('target_path'))
        filepath_key = self.expression2str(self.get_param('data_key'))

        timeout = int(self.expression2str(self.get_param('timeout'))) if self.has_param('timeout') else 30

        found = OSUtils.wait_for_file_within_seconds(source_file, timeout)
        if found:
            OSUtils.create_folder_if_not_existed(os.path.dirname(target_file))
            OSUtils.copy_file(source_file, target_file)
            logging.info('File copied: %s -> %s', source_file, target_file)
        else:
            logging.warning('File not found within %ds: %s', timeout, source_file)

        self.populate_data(filepath_key, target_file)
