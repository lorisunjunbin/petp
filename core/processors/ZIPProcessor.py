import logging
import os
import zipfile

from core.processor import Processor


class ZIPProcessor(Processor):
    TPL: str = '{"sourcefolder":"","sourcelist":"|","zipname":"", "pathinzip":"","targetfolder":"", "data_key":""}'
    DESC: str = f''' 
        Create zip file with name $zipname, and including either all files in $sourcefolder or files within $sourcelist; put the file to $targetfolder, also populate the data_key.   
        
        {TPL}
         
    '''

    def process(self):

        data_key = self.expression2str(self.get_param('data_key'))

        pathinzip = self.get_param('pathinzip') if self.has_param('pathinzip') else ''

        zipname = self.expression2str(self.get_param('zipname'))

        targetfolder = self.get_param('targetfolder')

        sourcefolder = self.get_param('sourcefolder')
        sourcelistStr = self.get_param('sourcelist')
        sourcelist = self.str2list(sourcelistStr) if self.has_param(
            "sourcelist") and self.SEPARATOR != sourcelistStr else []

        targetfile = ''

        if len(sourcelist) > 0:
            targetfile = self.zipList(sourcelist, zipname, targetfolder, pathinzip)
        else:
            targetfile = self.zipDir(sourcefolder, zipname, targetfolder, pathinzip)

        if not data_key is None:
            self.populate_data(data_key, targetfile)

    # zip a list of files
    def zipList(self, sourcelist, zipname, targetfolder, pathinzip):
        targetzip = targetfolder + zipname + '.zip'
        with zipfile.ZipFile(targetzip, 'w') as zf:
            for file in sourcelist:
                basename = os.path.basename(file)
                logging.info(file)
                zf.write(file, pathinzip + basename if len(pathinzip) > 0 else basename)
        return targetzip

    # zip entire folder
    def zipDir(self, sourcefolder, zipname, targetfolder, pathinzip):
        targetzip = targetfolder + zipname + '.zip'
        with zipfile.ZipFile(targetzip, 'w') as zf:
            for file in os.listdir(sourcefolder):
                logging.info(file)
                zf.write(sourcefolder + file, pathinzip + file if len(pathinzip) > 0 else file)
        return targetzip
