import logging
import shlex
import subprocess
import sys

from core.processor import Processor


class CMDProcessor(Processor):
    TPL: str = '{"cmdstr":"","cmddir":"","data_key":"", "timeout":30, "shell":"no", "encoding":"utf-8"}'
    DESC: str = '''
        Run system command via subprocess.check_output, then save the output to data_chain associated with data_key.

        Default behavior splits cmdstr with shlex (no shell, no metacharacter interpretation) — safe against ;|& injection.
        Set shell="yes" only when shell features (pipes, redirects, glob) are required and the command is fully trusted.

        - cmdstr: command string to execute (supports expression)
        - cmddir: working directory for the command (supports expression, optional)
        - data_key: key of data_chain to store the command output (supports expression, optional)
        - timeout: command execution timeout in seconds (default: 30, set empty to disable)
        - shell: "yes" to run via shell — DANGEROUS, disables injection protection (default: "no")
        - encoding: output encoding for decoding byte results (default: "utf-8")
    '''

    def get_category(self) -> str:
        return super().CATE_GENERAL

    def process(self):
        data_key = self.expression2str(self.get_param('data_key'))
        cmdstr = self.expression2str(self.get_param('cmdstr'))

        _cwd = self.expression2str(self.get_param("cmddir")) if self.has_param("cmddir") else None

        _shell = 'yes' == self.get_param('shell').lower() if self.has_param("shell") else False

        _encoding = self.explain_param_or_default("encoding", 'utf-8')

        _timeout = int(self.expression2str(self.get_param("timeout"))) if self.has_param("timeout") else None

        logging.info('CMD: %s (cwd=%s, shell=%s)', cmdstr, _cwd, _shell)

        if _shell:
            # Caller explicitly opted into shell. Metacharacters interpreted; cmdstr must be trusted.
            cmd_arg = cmdstr
        else:
            # Tokenize via shlex — ;, |, & become literal arguments, not shell directives.
            cmd_arg = shlex.split(cmdstr, posix=(sys.platform != 'win32'))

        stdout = subprocess.check_output(cmd_arg, stderr=subprocess.STDOUT, shell=_shell, timeout=_timeout, cwd=_cwd)

        if type(stdout) is str:
            output_str = stdout.strip('\n')
        elif type(stdout) is bytes:
            output_str = stdout.decode(_encoding).strip('\n')

        logging.debug('CMD output: %s', output_str)
        if not data_key is None:
            self.populate_data(data_key, output_str)
