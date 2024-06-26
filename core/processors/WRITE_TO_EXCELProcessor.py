from core.processor import Processor
from utils.ExcelUtil import ExcelUtil


class WRITE_TO_EXCELProcessor(Processor):
    TPL: str = '{"file_path":"", "value_key":"sheetname2list", "data_key":""}'
    DESC: str = f'''
        value_key point to the dict[str:[]] of data_chain, sheet title is key of the dict , sheet content list is value of dict.
        data_key is the key of data_chain to store the file_path.
        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_EXCEL

    def process(self):
        file_path = self.expression2str(self.get_param('file_path'))
        data_key = self.expression2str(self.get_param('data_key'))
        value_key = self.expression2str(self.get_param('value_key'))
        value_data = self.get_data(value_key)

        sheetname2list: dict[str:[]] = value_data if type(value_data) == dict \
            else {value_key: value_data} if type(value_data) == list else {}

        ExcelUtil.write_dict_to_excel(file_path, sheetname2list)

        self.populate_data(data_key, file_path)
