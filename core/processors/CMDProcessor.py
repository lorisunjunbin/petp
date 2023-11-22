import logging
import subprocess
import sys

from core.processor import Processor


class CMDProcessor(Processor):
    TPL: str = '{"cmdstr":"","cmddir":"","data_key":"", "timeout":30}'
    DESC: str = f''' 
        - Run system command via subprocess.check_output, then save value to data_chain associated with data_key. 
        
        {TPL}
        - cmdstr: command to execute
        - cmddir: which folder to run the cmd
         
    '''

    def get_category(self) -> str:
        return super().CATE_GENERAL

    def process(self):
        data_key = self.expression2str(self.get_param('data_key'))
        cmdstr = self.expression2str(self.get_param('cmdstr'))

        _cwd = self.expression2str(self.get_param("cmddir")) if self.has_param("cmddir") else None

        _shell = 'yes' == self.get_param('shell') if self.has_param("shell") else False

        _encoding = self.expression2str(self.get_param("encoding")) if self.has_param(
            "encoding") else sys.stdout.encoding

        _timeout = self.get_param("timeout") if self.has_param("timeout") else None

        logging.debug(f'>{cmdstr}, in folder {_cwd}')

        stdout = subprocess.check_output(cmdstr, stderr=subprocess.STDOUT, shell=True, timeout=_timeout, cwd=_cwd)

        if type(stdout) is str:
            output_str = stdout.strip('\n')
        elif type(stdout) is bytes:
            output_str = stdout.decode(_encoding).strip('\n')

        logging.debug(f'>{cmdstr} -> {output_str}')
        if not data_key is None:
            self.populate_data(data_key, output_str)
