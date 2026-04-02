import logging
import os
import subprocess

from core.processor import Processor
from utils.OSUtils import OSUtils


class OPEN_FILEProcessor(Processor):
    TPL: str = '{"file_path":"","file_path_key":"","timeout":10}'

    DESC: str = f'''
        Open a file using the system's default application. Waits for the file to exist within the given timeout.
        The file path can be provided directly or retrieved from data_chain via a key.

        - file_path: direct path to the file to open (supports expression, default: "")
        - file_path_key: key in data_chain whose value is used as the file path when file_path is empty (supports expression, default: "")
        - timeout: maximum seconds to wait for the file to exist before attempting to open it (default: 10)

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):
        file_path = self.expression2str(self.get_param('file_path'))
        if file_path is None or not len(file_path) > 0:
            file_path_key = self.expression2str(self.get_param('file_path_key'))
            file_path = self.get_data(file_path_key)

        timeout = self.get_param('timeout') if self.has_param('timeout') else 10
        found = OSUtils.wait_for_file_within_seconds(file_path, timeout)
        if found:
            logging.debug(f'=========\n going to open file: \n{file_path}\n===========================')
            if OSUtils.get_system() == 'darwin':
                subprocess.call(["open", file_path])
            else:
                os.startfile(file_path)
        else:
            logging.warning(f'\n\n=========\n not existed, timeout is {timeout}s, \n{file_path}\n=========\n')
