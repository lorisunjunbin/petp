import logging

from core.processor import Processor
from utils.ParamikoUtil import ParamikoUtil
from paramiko.client import SSHClient


class RUN_SSH_COMMANDProcessor(Processor):
    TPL: str = '{"ssh_client_key":"sshclient", "cmd":"", "data_key":"", "close_after_run":"yes|no"}'
    DESC: str = '''
        Run SSH command via paramiko, save result to data_key of data_chain.

        - ssh_client_key: key of data_chain where the SSH client instance is stored (default: "sshclient")
        - cmd: SSH command to execute (supports expression)
        - data_key: key of data_chain to store the command output
        - close_after_run: "yes" to close the SSH client after running the command, "no" to keep it open (default: "yes")
    '''
    def get_category(self) -> str:
        return super().CATE_PARAMIKO

    def process(self):

        ssh_client: SSHClient = self.get_data(self.get_param("ssh_client_key"))

        if not ssh_client is None:
            cmd = self.expression2str(self.get_param("cmd"))
            output_key = self.get_param("data_key")

            logging.info('SSH CMD: %s', cmd)
            output = ParamikoUtil.run_ssh_cmd(ssh_client, cmd)
            logging.debug('SSH output: %s', output)
            self.populate_data(output_key, output)

            close_after_run = True if self.get_param("close_after_run") == "yes" else False

            if close_after_run:
                ParamikoUtil.close_ssh_client(ssh_client)
        else:
            logging.warning('ssh_client is not available, please use CREATE_SSH_CLIENT task to setup.')
