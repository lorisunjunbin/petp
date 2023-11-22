from core.processor import Processor
from utils.ParamikoUtil import ParamikoUtil


class CREATE_SSH_CLIENTProcessor(Processor):
    TPL: str = '{"ssh_ip":"", "uname":"", "pwd":"","ssh_client_key":"sshclient"}'
    DESC: str = f''' 
        - Create paramiko ssh client, save to data_chain associated with ssh_client_key. 
        
        {TPL}
         
    '''
    def get_category(self) -> str:
        return super().CATE_PARAMIKO

    def process(self):

        dk = self.get_param("ssh_client_key")
        ip = self.expression2str(self.get_param("ssh_ip"))
        uname = self.expression2str(self.get_param("uname"))
        pwd = self.expression2str(self.get_param("pwd"))

        ssh_client = ParamikoUtil.get_ssh_client(ip, uname, pwd)

        if ssh_client is None:
            raise Exception(f'ssh_client is NOT able to create.')

        self.populate_data(dk, ssh_client)
