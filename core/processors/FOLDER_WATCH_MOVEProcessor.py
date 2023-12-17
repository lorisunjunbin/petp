import logging
import os
import shutil

from core.processor import Processor
from utils.OSUtils import OSUtils


class FOLDER_WATCH_MOVEProcessor(Processor):
    TPL: str = '{"sourcefolder":"","targetfolder":"endwith/","expectcount":"{10}", "targetfilespath_key":"", "timeout":30}'
    DESC: str = f'''

        Move file from [sourcefolder] to [targetfolder], wait until reaching the [expectcount] OR [timeout], 
        then save target file location to [targetfilespath_key] of data_chain. 

        {TPL}
        
    '''

    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):

        source_folder = self.expression2str(self.get_param('sourcefolder'))
        target_folder = self.expression2str(self.get_param('targetfolder'))
        expect_count = int(self.expression2str(self.get_param('expectcount'))) if self.has_param('expectcount') else 0
        target_filespath_key = self.expression2str(self.get_param('targetfilespath_key'))
        timeout = self.get_param('timeout') if self.has_param('timeout') else 2

        targetfiles_path = []

        if expect_count > 0:
            actual_file_count = OSUtils.wait_for_folder_reach_expectcount_within_seconds(source_folder, expect_count,
                                                                                         timeout)
            # move files if count matched with expected
            if actual_file_count == expect_count:
                targetfiles_path = self.move_files_only(source_folder, target_folder)
            else:
                logging.warning(f'expect {expect_count} files in {source_folder}, found {actual_file_count}')
        # move all files if no expected count
        else:
            targetfiles_path = self.move_files_only(source_folder, target_folder)

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
