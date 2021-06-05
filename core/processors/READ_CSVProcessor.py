from core.processor import Processor
from utils.ExcelUtil import ExcelUtil


class READ_CSVProcessor(Processor):
    TPL: str = '{"file_path":"", "file_path_key":"str on data_chain", "skip_first":"Yes|No", "data_key":"name on data_chain", "delimiter":"default is tab"}'

    DESC: str = f''' 
        
        Load csv file from location, read data into array and save to data_chain. 
        Support specific delimiter, default is tab. Able to skip the first row.

        {TPL}

    '''
    def process(self):
        skipFirst = True if self.get_param('skip_first') == 'Yes' else False

        fp = self.get_data(self.get_param('file_path_key')) if self.has_param('file_path_key') \
            else self.expression2str(self.get_param('file_path'))

        delimiter = self.get_param('delimiter') if self.has_param('delimiter') \
            else None

        data = ExcelUtil.get_data_from_csv(fp, skipFirst) if delimiter == None \
            else ExcelUtil.get_data_from_csv(fp, skipFirst, delimiter)

        self.populate_data(self.get_param('data_key'), data)
