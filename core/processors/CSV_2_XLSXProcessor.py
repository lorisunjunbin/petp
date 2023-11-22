from core.processor import Processor
from utils.ExcelUtil import ExcelUtil


class CSV_2_XLSXProcessor(Processor):
    TPL: str = '{"csv_file_path":"", "xlsx_file_path":"", "target_xlsx_key":"", "dlr":""}'
    DESC: str = f'''
        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_EXCEL

    def process(self):
        csv_file_path = self.expression2str(self.get_param('csv_file_path'))
        xlsx_file_path = self.expression2str(self.get_param('xlsx_file_path'))
        target_xlsx_key = self.expression2str(self.get_param('target_xlsx_key'))
        dlr = self.expression2str(self.get_param('dlr'))

        ExcelUtil.convert_csv_to_xlsx(csv_file_path, xlsx_file_path, dlr)
        self.populate_data(target_xlsx_key, xlsx_file_path)
