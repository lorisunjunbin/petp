import logging

from core.processor import Processor
from utils.OSUtils import OSUtils


class FIND_FILESProcessor(Processor):
    TPL: str = '{"path_to_find":"", "file_name_lambda":"len(file_name) > 1", "depth_lambda":"depth == 1", "found_file_key":"found_file"}'

    DESC: str = f'''
        Recursively collect files from a directory using configurable lambda filters for file name and directory depth.
        The list of found file paths is stored in data_chain under the specified key.

        - path_to_find: root directory path to search for files (supports expression, default: "")
        - file_name_lambda: Python lambda expression as a string to filter files by name; evaluated with variable file_name (supports expression, default: "len(file_name) > 1")
        - depth_lambda: Python lambda expression as a string to filter by directory depth; evaluated with variable depth (supports expression, default: "depth == 1")
        - found_file_key: key in data_chain to store the list of found file paths (supports expression, default: "found_file")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):
        path_to_find = self.expression2str(self.get_param('path_to_find'))
        file_name_lambda_str = self.expression2str(self.get_param('file_name_lambda'))
        depth_lambda_str = self.expression2str(self.get_param('depth_lambda'))
        found_file_key = self.expression2str(self.get_param('found_file_key'))

        depth_lambda = lambda depth: eval(depth_lambda_str)
        file_name_lambda = lambda file_name: eval(file_name_lambda_str)

        found = OSUtils.collect_files(path_to_find, depth_lambda, file_name_lambda)

        logging.info('Found %d files in: %s', len(found), path_to_find)
        logging.debug('Found files: %s', found)

        self.populate_data(found_file_key, found)
