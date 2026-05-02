import logging
import os
import zipfile

from core.processor import Processor


class UNZIPProcessor(Processor):
    TPL: str = '{"path_to_zip_file":"", "directory_to_extract":"", "path_after_extract_key":"path_after_extract", "pwd":"", "name_appended":""}'

    DESC: str = f'''
        Simply unzip the file from path_to_zip_file to directory_to_extract, if protected with password, use pwd.
        path_after_extract_key is key of data_chain, points to final path after unzip.
        name_appended will be appended to directory_to_extract.

        - path_to_zip_file: source zip file path to extract (supports expression, default: "")
        - directory_to_extract: target directory where files are extracted to (supports expression, default: "")
        - path_after_extract_key: key in data_chain to store the final extraction path (supports expression, default: "path_after_extract")
        - pwd: password for protected zip files (supports expression, default: "")
        - name_appended: sub-path appended to directory_to_extract to form the final path (supports expression, default: "")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_ZIP

    def process(self):
        path_to_zip_file = self.expression2str(self.get_param('path_to_zip_file'))

        directory_to_extract = self.expression2str(self.get_param('directory_to_extract'))
        path_after_extract_key = self.expression2str(self.get_param('path_after_extract_key'))

        name_appended = self.explain_param_or_default('name_appended', '')
        pwd = bytes(str(self.expression2str(self.get_param('pwd'))), 'utf-8') if self.has_param("pwd") else None

        with zipfile.ZipFile(path_to_zip_file, 'r') as zf:
            zf.extractall(directory_to_extract, None, pwd)

        final_path = os.path.join(directory_to_extract, name_appended)

        logging.info(f'{path_after_extract_key} is {final_path}')

        self.populate_data(path_after_extract_key, final_path)
