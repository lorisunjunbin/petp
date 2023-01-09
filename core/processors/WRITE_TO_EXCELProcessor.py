from core.processor import Processor
from utils.ExcelUtil import ExcelUtil


class WRITE_TO_EXCELProcessor(Processor):
    TPL: str = '{"file_path":"", "value_key":"sheetname2list", "data_key":""}'
    DESC: str = f'''
        value_key point to the dict[str:[]] of data_chain, sheet title is key of the dict , sheet content list is value of dict.
        {TPL}
    '''

    def process(self):
        file_path = self.expression2str(self.get_param('file_path'))

        sheetname2list: dict[str:[]] = self.get_data(self.get_param('value_key'))

        ExcelUtil.write_dict_to_excel(file_path, sheetname2list)

        self.populate_data(self.get_param('data_key'), file_path)
