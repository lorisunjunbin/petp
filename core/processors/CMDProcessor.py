import logging
import subprocess
import sys

from core.processor import Processor


class CMDProcessor(Processor):
    TPL: str = '{"cmdstr":"","cmddir":"","shell":"yes|no","encoding":"utf-8", "runonly":"yes|no", "data_key":""}'
    DESC: str = f''' 
        - Run system command via subprocess.check_output, then save value to data_chain associated with data_key. 
        
        {TPL}
        - cmddir: which folder to run the cmd
        - shell: yes to run cmd as a system command, default is False
        
        {{"cmdstr":"curl ifconfig.co", "data_key":"myip", "cmddir":"", "shell":"yes|no", "encoding":"utf-8", "runonly":"yes|no"}}
        means:         
        >curl ifconfig.co 
        >192.168.1.1
        add key-value "myip": "192.168.1.1" to data_chain.
         
    '''

    def process(self):

        data_key = self.expression2str(self.get_param('data_key'))
        cmdstr = self.expression2str(self.get_param('cmdstr'))
        runonly = self.expression2str(self.get_param('runonly'))
        _cwd = self.expression2str(self.get_param("cmddir")) if self.has_param("cmddir") else None
        _shell = 'yes' == self.get_param('shell') if self.has_param("shell") else False
        _encoding = self.expression2str(self.get_param("encoding")) if self.has_param(
            "encoding") else sys.stdout.encoding

        params = []
        if not cmdstr is None:
            params = cmdstr.split(' ')
        else:
            cmd = self.expression2str(self.get_param('cmd'))
            input = self.expression2str(self.get_param('input'))
            params.append(cmd)
            if not input is None:
                params.append(input)

        logging.info(f'>{params}')

        if 'yes' == runonly:
            returnpack = subprocess.run(params, stdin=None, cwd=_cwd, encoding=_encoding, shell=_shell, stderr=None,
                                    universal_newlines=False)
            logging.info(f'>{params} in folder: {_cwd}  ->  {returnpack}')
            if not data_key is None:
                self.populate_data(data_key, returnpack.returncode)

        else:
            stdout = subprocess.check_output(params, stdin=None, cwd=_cwd, encoding=_encoding, shell=_shell, stderr=None,
                                             universal_newlines=False)
            outputStr = ''
            if type(stdout) is str:
                outputStr = stdout.strip('\n')
            elif type(stdout) is bytes:
                outputStr = stdout.decode(_encoding).strip('\n')
            logging.info(f'>{params} -> {outputStr}')
            if not data_key is None:
                self.populate_data(data_key, outputStr)
