from core.processor import Processor


class READ_TEXT_FROM_FILEProcessor(Processor):
    TPL: str = '{"file_path":"","data_key":""}'
    DESC: str = f'''
        Read file content as text from [file_path] , then save to [data_key] of data_chain.

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):
        file_path = self.expression2str(self.get_param('file_path'))
        data_key = self.expression2str(self.get_param('data_key'))

        with open(file_path, "r+", encoding='utf8') as text_file:
            self.populate_data(data_key, text_file.read())
