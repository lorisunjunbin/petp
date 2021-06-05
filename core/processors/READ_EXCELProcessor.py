from core.processor import Processor
from utils.ExcelUtil import ExcelUtil


class READ_EXCELProcessor(Processor):
    TPL: str = '{"file_path":"", "file_path_key":"str on data_chain", "skip_first":"yes|no", "data_key":"name on data_chain"}'
    DESC: str = f''' 

        Load MS Excel file from location, read data into array and save to data_chain. 
        Able to skip the first row.

        {TPL}

    '''
    def process(self):
        skipFirst = True if self.get_param('skip_first') == 'yes' else False
        fp = self.get_data(self.get_param('file_path_key')) if self.has_param('file_path_key') \
            else self.expression2str(self.get_param('file_path'))

        data = ExcelUtil.get_data_from_excel_file(fp, 1 if skipFirst else 0)

        self.populate_data(self.get_param('data_key'), data)
