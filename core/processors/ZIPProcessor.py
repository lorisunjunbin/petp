import logging
import glob
import os
import zipfile

from core.processor import Processor
from utils.OSUtils import OSUtils


class ZIPProcessor(Processor):
    TPL: str = '{"sourcefolder":"","sourcelist":"|","zipname":"", "pathinzip":"","pathbereplaced":"","targetfolder":"", "data_key":""}'
    DESC: str = f''' 
        Create zip file with name $zipname, and including either all files in $sourcefolder or files within $sourcelist; put the file to $targetfolder, also populate the data_key.   
        pathbereplaced will be replaced by pathinzip or removed if pathinzip is empty. 
        {TPL}
         
    '''

    def get_category(self) -> str:
        return super().CATE_ZIP

    def process(self):

        data_key = self.expression2str(self.get_param('data_key'))

        pathinzip = self.expression2str(self.get_param('pathinzip')) if self.has_param('pathinzip') else ''

        pathbereplaced = self.expression2str(self.get_param('pathbereplaced')) \
            if self.has_param('pathbereplaced') \
            else ''

        zipname = self.expression2str(self.get_param('zipname'))

        targetfolder = self.expression2str(self.get_param('targetfolder'))
        OSUtils.create_folder_if_not_existed(targetfolder)

        sourcefolder = self.expression2str(self.get_param('sourcefolder'))
        sourcelistStr = self.expression2str(self.get_param('sourcelist'))

        sourcelist = self.str2list(sourcelistStr) if self.has_param(
            "sourcelist") and self.SEPARATOR != sourcelistStr else []

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
