import logging

from core.processor import Processor
from utils.OSUtils import OSUtils


class FIND_FILESProcessor(Processor):
    TPL: str = '{"path_to_find":"", "file_name_lambda":"len(file_name) > 1", "depth_lambda":"depth == 1", "found_file_key":"found_file"}'

    DESC: str = f''' 
        Collect files from path_to_find with depth and file_name filter
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

        logging.info(f"Found {len(found)} files: {str(found)}")

        self.populate_data(found_file_key, found)
