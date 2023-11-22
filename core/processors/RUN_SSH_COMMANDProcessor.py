import logging

from core.processor import Processor
from utils.ParamikoUtil import ParamikoUtil
from paramiko.client import SSHClient


class RUN_SSH_COMMANDProcessor(Processor):
    TPL: str = '{"ssh_client_key":"sshclient", "cmd":"", "output_key":"", "close_after_run":"yes|no"}'
    DESC: str = f''' 
        - run ssh via paramiko, save result to output_key of data_chain. 

        {TPL}

    '''
    def get_category(self) -> str:
        return super().CATE_PARAMIKO

    def process(self):

        ssh_client: SSHClient = self.get_data(self.get_param("ssh_client_key"))

        if not ssh_client is None:
            cmd = self.expression2str(self.get_param("cmd"))
            output_key = self.get_param("output_key")

            output = ParamikoUtil.run_ssh_cmd(ssh_client, cmd)
            self.populate_data(output_key, output)

            close_after_run = True if self.get_param("close_after_run") == "yes" else False

            if close_after_run:
                ParamikoUtil.close_ssh_client(ssh_client)
        else:
            logging.warning('ssh_client is not available, please use CREATE_SSH_CLIENT task to setup.')
