from core.processor import Processor


class WRITE_TO_FILEProcessor(Processor):
    TPL: str = '{"file_path":"", "content":"", "data_key":""}'
    DESC: str = f'''
        Write [content] to [file_path] , without error then target word file location will be saved to [data_key] of data_chain.

        {TPL}
    '''
    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):
        file_path = self.expression2str(self.get_param('file_path'))
        content = self.expression2str(self.get_param('content'))

        with open(file_path, "w", encoding='utf8') as text_file:
            text_file.write(content)

        self.populate_data(self.get_param('data_key'), file_path)
