import logging

from core.processor import Processor
from utils.ExcelUtil import ExcelUtil


class CSV_2_XLSXProcessor(Processor):
    TPL: str = '{"source_path":"", "target_path":"", "data_key":"", "delimiter":""}'
    DESC: str = '''
        Convert CSV file to XLSX format. Read from source_path, write to target_path, then save the target xlsx path to data_chain via data_key.

        - source_path: source CSV file path (supports expression)
        - target_path: target XLSX file path to write (supports expression)
        - data_key: key of data_chain to store the xlsx file path (supports expression)
        - delimiter: delimiter used in the CSV file, e.g. "," or "\\t" (supports expression)
    '''

    def get_category(self) -> str:
        return super().CATE_EXCEL

    def process(self):
        csv_file_path = self.expression2str(self.get_param('source_path'))
        xlsx_file_path = self.expression2str(self.get_param('target_path'))
        target_xlsx_key = self.expression2str(self.get_param('data_key'))
        dlr = self.expression2str(self.get_param('delimiter'))

        ExcelUtil.convert_csv_to_xlsx(csv_file_path, xlsx_file_path, dlr)
        logging.info('Converted CSV to XLSX: %s -> %s', csv_file_path, xlsx_file_path)
        self.populate_data(target_xlsx_key, xlsx_file_path)
