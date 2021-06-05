from core.processor import Processor
from utils.OSUtils import OSUtils


class FILE_WATCH_MOVEProcessor(Processor):
    TPL: str = '{"filename":"","movetofolder":"endwith/","targetname":"fstr", "filepath_key":"", "timeout":30}'
    DESC: str = f'''

        Move file from [filename] to [movetofolder + targetname], wait until [timeout], then save target location to [filepath_key] of data_chain. 

        {TPL}
        
    '''
    def process(self):
        source = self.expression2str(self.get_param('filename'))
        targetfolder = self.expression2str(self.get_param('movetofolder'))
        targetname = self.expression2str(self.get_param('targetname'))
        filepath_key = self.expression2str(self.get_param('filepath_key'))

        timeout = self.get_param('timeout') if self.has_param('timeout') else 30
        target = targetfolder + targetname

        found = OSUtils.wait_for_file_within_seconds(source, timeout)
        if found:
            OSUtils.copy_file(source, target)

        self.populate_data(filepath_key, target)
