import logging

from core.processor import Processor
from utils.ExcelUtil import ExcelUtil


class READ_CSVProcessor(Processor):
    TPL: str = '{"file_path":"", "file_path_key":"str on data_chain", "skip_first":"Yes|No", "data_key":"name on data_chain", "delimiter":"default is tab"}'

    DESC: str = '''
        Load CSV file from location, read data into 2D array and save to data_chain.

        - file_path: CSV file path (supports expression)
        - file_path_key: key of data_chain to get the file path, takes priority over file_path if set
        - skip_first: "Yes" to skip the first row (header), "No" to include it (default: "No")
        - data_key: key of data_chain to store the parsed CSV data
        - delimiter: column delimiter (default: tab)
    '''
    def get_category(self) -> str:
        return super().CATE_EXCEL

    def process(self):
        skipFirst = True if self.get_param('skip_first') == 'Yes' else False

        fp = self.get_data(self.get_param('file_path_key')) if self.has_param('file_path_key') \
            else self.expression2str(self.get_param('file_path'))

        delimiter = self.get_param('delimiter') if self.has_param('delimiter') \
            else None

        data = ExcelUtil.get_data_from_csv(fp, skipFirst) if delimiter == None \
            else ExcelUtil.get_data_from_csv(fp, skipFirst, delimiter)

        logging.info('Read CSV: %s (%d rows)', fp, len(data))
        self.populate_data(self.get_param('data_key'), data)
