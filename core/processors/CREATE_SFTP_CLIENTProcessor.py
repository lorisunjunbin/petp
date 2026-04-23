from core.processor import Processor
from utils.ParamikoUtil import ParamikoUtil


class CREATE_SFTP_CLIENTProcessor(Processor):
    TPL: str = '{"sftp_ip":"","sftp_port": 22, "uname":"", "pwd":"","sftp_client_key":"sftpclient"}'
    DESC: str = f'''
        Create paramiko SFTP client, save to data_chain associated with sftp_client_key.

        - sftp_ip: SFTP server IP address (supports expression)
        - sftp_port: SFTP server port (default: 22)
        - uname: username for authentication (supports expression)
        - pwd: password for authentication (supports expression)
        - sftp_client_key: key of data_chain to store the SFTP client instance (default: "sftpclient")

        {TPL}
    '''
    def get_category(self) -> str:
        return super().CATE_PARAMIKO

    def process(self):
        ip = self.expression2str(self.get_param("sftp_ip"))
        uname = self.expression2str(self.get_param("uname"))
        pwd = self.expression2str(self.get_param("pwd"))

        dk = self.get_param("sftp_client_key")
        port = int(self.expression2str(self.get_param("sftp_port")))

        sftp_client = ParamikoUtil.get_sftp_client(ip, uname, pwd, port)

        if sftp_client is None:
            raise Exception(f'sftp_client is NOT able to create.')

        self.populate_data(dk, sftp_client)
