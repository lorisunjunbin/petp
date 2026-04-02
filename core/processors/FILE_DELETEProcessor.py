from core.processor import Processor
from utils.OSUtils import OSUtils


class FILE_DELETEProcessor(Processor):
    TPL: str = '{"file_path":"path/to/folder/file"}'
    DESC: str = f'''
        Delete the file at the given absolute file_path.

        - file_path: absolute path of the file to delete (supports expression)

        {TPL}
    '''
    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):
        OSUtils.delete_file_if_existed(
            self.expression2str(
                self.get_param('file_path')
            )
        )
