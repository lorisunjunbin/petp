import logging
import glob
import os
import zipfile

from core.processor import Processor
from utils.OSUtils import OSUtils


class ZIPProcessor(Processor):
    TPL: str = '{"source_path":"","source_list":"|","zip_name":"", "path_in_zip":"","path_to_replace":"","target_path":"", "data_key":""}'
    DESC: str = '''
        Create a zip file with the given name, including either all files in source_path or specific files from source_list.
        The resulting zip is placed in target_path, and its path is stored in data_chain via data_key.
        path_to_replace will be replaced by path_in_zip inside the archive, or removed if path_in_zip is empty.

        - source_path: folder whose files are recursively zipped when source_list is not provided (supports expression, default: "")
        - source_list: pipe-separated list of specific file paths to include; falls back to source_path if only "|" (supports expression, default: "|")
        - zip_name: name of the output zip file (without extension) (supports expression, default: "")
        - path_in_zip: replacement path structure inside the zip archive (supports expression, default: "")
        - path_to_replace: portion of the file path to be replaced by path_in_zip within the archive (supports expression, default: "")
        - target_path: output directory where the zip file is created (supports expression, default: "")
        - data_key: key in data_chain to store the resulting zip file path (supports expression, default: "")
    '''

    def get_category(self) -> str:
        return super().CATE_ZIP

    def process(self):

        data_key = self.expression2str(self.get_param('data_key'))

        pathinzip = self.explain_param_or_default('path_in_zip', '')

        pathbereplaced = self.explain_param_or_default('path_to_replace', '')

        zipname = self.expression2str(self.get_param('zip_name'))

        targetfolder = self.expression2str(self.get_param('target_path'))
        OSUtils.create_folder_if_not_existed(targetfolder)

        sourcefolder = self.expression2str(self.get_param('source_path'))
        sourcelistStr = self.expression2str(self.get_param('source_list'))

        sourcelist = self.str2list(sourcelistStr) if self.has_param(
            "source_list") and self.SEPARATOR != sourcelistStr else []

        targetfile = self.zipList(sourcelist, zipname, targetfolder, pathbereplaced, pathinzip) \
            if len(sourcelist) > 0 \
            else self.zipDir(sourcefolder, zipname, targetfolder, pathbereplaced, pathinzip)

        if not data_key is None:
            self.populate_data(data_key, targetfile)

    # zip a list of files
    def zipList(self, sourcelist, zipname, targetfolder, pathbereplaced, pathinzip):
        targetzip = targetfolder + zipname + '.zip'
        with (zipfile.ZipFile(targetzip, 'w') as zf):
            for file in sourcelist:
                filepathinzip = file.replace(pathbereplaced, pathinzip) \
                    if len(pathinzip) > 0 \
                    else file.replace(pathbereplaced, '')
                logging.debug(f'append {file} into filepathinzip: {filepathinzip}')
                zf.write(file, filepathinzip)

        return targetzip

    # zip entire folder
    def zipDir(self, sourcefolder, zipname, targetfolder, pathbereplaced, pathinzip):
        sourcelist = []

        for filename in glob.iglob(sourcefolder + '**/**', recursive=True):
            if filename not in sourcelist and os.path.isfile(filename):
                sourcelist.append(filename)

        logging.debug(str(sourcelist))

        return self.zipList(sourcelist, zipname, targetfolder, pathbereplaced, pathinzip)
