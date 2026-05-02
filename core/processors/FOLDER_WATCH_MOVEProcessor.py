import logging
import os
import time

from core.processor import Processor
from utils.OSUtils import OSUtils


class FOLDER_WATCH_MOVEProcessor(Processor):
    TPL: str = '{"source_path":"","target_path":"endwith/","expect_count":"{10}", "data_key":"", "timeout":30}'
    DESC: str = f'''
        Move files from source folder to target folder. Supports waiting for expected file count or timeout before moving.

        - source_path: source folder path to watch (supports expression)
        - target_path: target folder path to move files to (supports expression)
        - expect_count: expected number of files to wait for before moving (default: "{10}")
        - data_key: key of data_chain to store the list of moved file paths (supports expression)
        - timeout: max seconds to wait for files (default: 30)

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):

        source_folder = self.expression2str(self.get_param('source_path'))
        target_folder = self.expression2str(self.get_param('target_path'))
        expect_count = int(self.expression2str(self.get_param('expect_count'))) if self.has_param('expect_count') else 0
        target_filespath_key = self.expression2str(self.get_param('data_key'))
        timeout = self.explain_param_as_int('timeout', 2)

        logging.info(f'source_folder={source_folder}')
        logging.info(f'target_folder={target_folder}')
        logging.info(f'target_filespath_key={target_filespath_key}')

        targetfiles_path = []

        if expect_count > 0:
            actual_file_count = OSUtils.wait_for_folder_reach_expectcount_within_seconds(source_folder, expect_count,
                                                                                         timeout)

            # move files if count matched with expected
            if actual_file_count == expect_count:
                targetfiles_path = self.move_files_only(source_folder, target_folder)
                logging.info(f'count matched,  targetfiles_path={targetfiles_path}')
            else:
                logging.warning(
                    f'expect {expect_count} files in {source_folder}, found {actual_file_count}, will not move')

        # move all files if no expected count, but wait for timeout if specified
        elif timeout > 0:
            time.sleep(timeout)
            targetfiles_path = self.move_files_only(source_folder, target_folder)
            logging.info(f'wait {timeout} seconds,  targetfiles_path={targetfiles_path}')
        # move all files if no expected count
        else:
            targetfiles_path = self.move_files_only(source_folder, target_folder)
            logging.info(f'timeout:{timeout}, expect_count:{expect_count},  targetfiles_path={targetfiles_path}')

        self.populate_data(target_filespath_key, targetfiles_path)

    def move_files_only(self, source_folder, target_folder):
        resut = []
        for f in os.listdir(source_folder):
            sourcefile_path = os.path.join(source_folder, f)
            if os.path.isfile(sourcefile_path):
                targetfile_path = os.path.join(target_folder, f)
                # create target folder if not existed
                OSUtils.create_folder_if_not_existed(target_folder)
                # move file
                OSUtils.copy_file(sourcefile_path, targetfile_path)
                OSUtils.delete_file_if_existed(sourcefile_path)
                logging.debug(f'moving {f} to {targetfile_path}')
                resut.append(targetfile_path)

        return resut
