import logging
import os

from core.processor import Processor


class FIND_LATEST_FILEProcessor(Processor):
    TPL: str = '{"path_to_find":"", ' \
               '"file_type":".zip",' \
               '"found_file_key":"found_file" ' \
               '}'

    DESC: str = f''' 
        finding the latest file of a given type (file_type) in specific folder(path_to_find)
        found_file_key is the key of data_chain which points to full file path
        {TPL}
         
    '''

    def process(self):
        path_to_find = self.expression2str(self.get_param('path_to_find'))
        file_type = self.expression2str(self.get_param('file_type'))
        found_file_key = self.expression2str(self.get_param('found_file_key'))

        logging.info(f'Searching for the latest {file_type} in {path_to_find}')

        files = [
            (f, os.path.getmtime(os.path.join(path_to_find, f)))
            for f in os.listdir(path_to_find)
            if os.path.isfile(os.path.join(path_to_find, f)) and f.endswith(file_type)
        ]

        files.sort(key=lambda x: x[1], reverse=True)

        file_path_found = os.path.join(path_to_find, files[0][0]) if len(files) > 0 else 'FILE_NOT_FOUND'

        logging.info(f'Found newest {file_type} file in {path_to_find} is {file_path_found}')

        self.populate_data(found_file_key, file_path_found)
