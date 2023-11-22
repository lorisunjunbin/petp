import logging
import os
import zipfile

from core.processor import Processor


class UNZIPProcessor(Processor):
    TPL: str = '{"path_to_zip_file":"", ' \
               '"directory_to_extract":"",' \
               '"path_after_extract_key":"path_after_extract", ' \
               '"pwd":"", ' \
               '"name_appended":""}'

    DESC: str = f''' 
        Simply unzip the file from path_to_zip_file to directory_to_extract, if protected with password, use pwd.
        path_after_extract_key is key of data_chain, points to final path after unzip.   
        name_appended will be appended to directory_to_extract.
        
        {TPL}
         
    '''

    def get_category(self) -> str:
        return super().CATE_ZIP

    def process(self):
        path_to_zip_file = self.expression2str(self.get_param('path_to_zip_file'))

        directory_to_extract = self.expression2str(self.get_param('directory_to_extract'))
        path_after_extract_key = self.expression2str(self.get_param('path_after_extract_key'))

        name_appended = self.expression2str(self.get_param('name_appended')) if self.has_param("name_appended") else ''
        pwd = self.expression2str(self.get_param('pwd'))

        with zipfile.ZipFile(path_to_zip_file, 'r') as zip_file_ref:
            zip_file_ref.extractall(directory_to_extract, pwd=pwd)

        final_path = os.path.join(directory_to_extract, name_appended)

        logging.debug(f'{path_after_extract_key} is {final_path}')

        self.populate_data(path_after_extract_key, final_path)
