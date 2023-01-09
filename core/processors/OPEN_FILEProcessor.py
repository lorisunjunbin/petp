import logging
import os
import subprocess

from core.processor import Processor
from utils.OSUtils import OSUtils


class OPEN_FILEProcessor(Processor):
    TPL: str = '{"file_path":"","file_path_key":"","timeout":10}'

    DESC: str = f''' 
        - Try to open file via system tool. 
        {TPL}
    '''

    def process(self):
        file_path = self.expression2str(self.get_param('file_path'))
        if file_path is None or not len(file_path) > 0:
            file_path_key = self.expression2str(self.get_param('file_path_key'))
            file_path = self.get_data(file_path_key)

        timeout = self.get_param('timeout') if self.has_param('timeout') else 10
        found = OSUtils.wait_for_file_within_seconds(file_path, timeout)
        if found:
            logging.info(f'\n\n=========\n going to open file: \n{file_path}\n=========\n')
            if OSUtils.get_sytem() == 'darwin':
                subprocess.call(["open", file_path])
            else:
                os.startfile(file_path)
        else:
            logging.warning(f'\n\n=========\n not existed, timeout is {timeout}s, \n{file_path}\n=========\n')
