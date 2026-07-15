import logging

from paramiko.sftp_client import SFTPClient

from core.processor import Processor
from utils.ParamikoUtil import ParamikoUtil


class RUN_SFTP_GETProcessor(Processor):
    TPL: str = '{"from_remote":"","to_local": "","sftp_client_key":"sftpclient", "sftp_get_file_key":"", "close_after_run":"yes|no"}'
    DESC: str = '''
        Get (download) file from remote server to local via paramiko SFTP client.

        - from_remote: remote file path to download (supports expression)
        - to_local: local file path to save the downloaded file (supports expression)
        - sftp_client_key: key of data_chain where the SFTP client instance is stored (default: "sftpclient")
        - sftp_get_file_key: key of data_chain to store the local file path after download
        - close_after_run: "yes" to close the SFTP client after download, "no" to keep it open (default: "yes")
    '''
    def get_category(self) -> str:
        return super().CATE_PARAMIKO

    def process(self):

        sftp_client: SFTPClient = self.get_data(self.get_param("sftp_client_key"))
        if not sftp_client is None:

            from_remote = self.expression2str(self.get_param("from_remote"))
            to_local = self.expression2str(self.get_param("to_local"))
            close_after_run = True if self.get_param("close_after_run") == "yes" else False
            sftp_get_file_key = self.get_param("sftp_get_file_key")

            ParamikoUtil.run_sftp_get(sftp_client, from_remote, to_local)
            logging.info('SFTP GET: %s -> %s', from_remote, to_local)
            self.populate_data(sftp_get_file_key, to_local)

            if close_after_run:
                ParamikoUtil.close_sftp_client(sftp_client)
        else:
            logging.warning('sftp_client is not available, please use CREATE_SFTP_CLIENT task to setup.')
