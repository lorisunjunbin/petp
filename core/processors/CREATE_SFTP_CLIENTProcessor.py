from core.processor import Processor
from utils.ParamikoUtil import ParamikoUtil


class CREATE_SFTP_CLIENTProcessor(Processor):
    TPL: str = '{"sftp_ip":"","sftp_port": 22, "uname":"", "pwd":"","sftp_client_key":"sftpclient"}'
    DESC: str = f''' 
        - Create paramiko sftp client, save to data_chain associated with sftp_client_key. 
        
        {TPL}
         
    '''

    def process(self):
        ip = self.expression2str(self.get_param("sftp_ip"))
        uname = self.expression2str(self.get_param("uname"))
        pwd = self.expression2str(self.get_param("pwd"))

        dk = self.get_param("sftp_client_key")
        port = self.get_param("sftp_port")

        sftp_client = ParamikoUtil.get_sftp_client(ip, uname, pwd, port)

        if sftp_client is None:
            raise Exception(f'sftp_client is NOT able to create.')

        self.populate_data(dk, sftp_client)
