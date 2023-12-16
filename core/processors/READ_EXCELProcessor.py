from core.processor import Processor
from utils.ExcelUtil import ExcelUtil


class READ_EXCELProcessor(Processor):
    TPL: str = '{"file_path":"", "fields":"unset OR Field1|Field2|", "sheet_index":0, "file_path_key":"str on data_chain", "end_at":"10", "skip_first":"yes|no", "data_key":"name on data_chain"}'

    DESC: str = f''' 

        Load MS Excel file from location, read data into array and save to data_chain. 
        Able to skip the first row.

        {TPL}

    '''
    def get_category(self) -> str:
        return super().CATE_EXCEL

    def process(self):
        skipFirst = True if self.get_param('skip_first') == 'yes' else False
        fields_str = self.get_param('fields')

        fp = self.get_data(self.get_param('file_path_key')) if self.has_param('file_path_key') \
            else self.expression2str(self.get_param('file_path'))

        sheet_index = self.get_param("sheet_index") if self.has_param("sheet_index") else 0

        end_at = int(self.expression2str(self.get_param('end_at'))) if self.has_param('end_at') else 10

        data = ExcelUtil.get_data_from_excel_file(fp, 1 if skipFirst else 0, end_at, sheet_index)

        if len(data) > 0 and \
                not skipFirst and \
                fields_str is not None and \
                len(fields_str) > 0:

            fields: [str] = fields_str.split(self.SEPARATOR)
            self.populate_data(self.get_param('data_key'), ExcelUtil.filter_by_fields(fields, data))
        else:
            self.populate_data(self.get_param('data_key'), data)
