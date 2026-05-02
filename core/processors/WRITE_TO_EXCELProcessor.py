import logging

from core.processor import Processor
from utils.ExcelUtil import ExcelUtil


class WRITE_TO_EXCELProcessor(Processor):
    TPL: str = '{"file_path":"", "value_key":"sheetname2list", "data_key":""}'
    DESC: str = '''
        Write data to an Excel file. The data is retrieved from data_chain via value_key, expected as a dict mapping
        sheet names (str) to row data (list). If the value is a plain list, it is wrapped using value_key as the sheet name.
        The resulting file path is stored back into data_chain via data_key.

        - file_path: output Excel file path to write to (supports expression, default: "")
        - value_key: key in data_chain pointing to the sheet data dict[str:list] or a plain list (supports expression, default: "sheetname2list")
        - data_key: key in data_chain to store the written file path (supports expression, default: "")
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
        logging.info('Written Excel: %s (%d sheets)', file_path, len(sheetname2list))
        self.populate_data(data_key, file_path)
