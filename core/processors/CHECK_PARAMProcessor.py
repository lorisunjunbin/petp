from core.processor import Processor


class CHECK_PARAMProcessor(Processor):
    TPL: str = '{"param_not_empty":"name1|>name2"}'
    DESC: str = f'''
        Check that required data_chain attributes exist and are non-empty. Terminates the execution if not satisfied.

        - param_not_empty: attribute name(s) to check, use ""{Processor.SEPARATOR}"" for nested access, e.g. "name1{Processor.SEPARATOR}name2"

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_GUI

    def process(self):
        paramnames = self.get_param('param_not_empty')
        data = self.get_deep_data(paramnames.split(self.SEPARATOR))

        if data == None or len(data) == 0:
            raise Exception(f'Parameter required: {paramnames} ')
