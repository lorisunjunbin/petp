import os.path

from core.processor import Processor
from utils.OSUtils import OSUtils


class FILE_WATCH_MOVEProcessor(Processor):
    TPL: str = '{"sourcefile":"","targetfile":"", "filepath_key":"", "timeout":30}'
    DESC: str = f'''

        Move file from [sourcefile] to [targetfile], wait until [timeout], then save target location to [filepath_key] of data_chain. 

        {TPL}
        
    '''

    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):
        source_file = self.expression2str(self.get_param('sourcefile'))
        target_file = self.expression2str(self.get_param('targetfile'))
        filepath_key = self.expression2str(self.get_param('filepath_key'))

        timeout = self.get_param('timeout') if self.has_param('timeout') else 30

        found = OSUtils.wait_for_file_within_seconds(source_file, timeout)
        if found:
            OSUtils.create_folder_if_not_existed(os.path.dirname(target_file))
            OSUtils.copy_file(source_file, target_file)

        self.populate_data(filepath_key, target_file)
