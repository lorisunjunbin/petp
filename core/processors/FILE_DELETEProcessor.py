from core.processor import Processor
from utils.OSUtils import OSUtils


class FILE_DELETEProcessor(Processor):
    TPL: str = '{"file_path":"path/to/folder/file"}'
    DESC: str = f'''
        To delete the file associated with given absolute file_path
        
        {TPL}
        
    '''

    def process(self):
        OSUtils.delete_file_if_existed(
            self.expression2str(
                self.get_param('file_path')
            )
        )
