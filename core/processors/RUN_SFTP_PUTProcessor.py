import logging

from paramiko.sftp_client import SFTPClient

from core.processor import Processor
from utils.ParamikoUtil import ParamikoUtil


class RUN_SFTP_PUTProcessor(Processor):
    TPL: str = '{"from_local":"","to_remote": "","sftp_client_key":"sftpclient", "sftp_put_file_key":"", "close_after_run":"yes|no"}'
    DESC: str = f'''
        Put (upload) file from local to remote server via paramiko SFTP client.

        - from_local: local file path to upload (supports expression)
        - to_remote: remote file path to save the uploaded file (supports expression)
        - sftp_client_key: key of data_chain where the SFTP client instance is stored (default: "sftpclient")
        - sftp_put_file_key: key of data_chain to store the remote file path after upload
        - close_after_run: "yes" to close the SFTP client after upload, "no" to keep it open (default: "yes")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_PARAMIKO

    def process(self):

        sftp_client: SFTPClient = self.get_data(self.get_param("sftp_client_key"))
        if not sftp_client is None:

            from_local = self.expression2str(self.get_param("from_local"))
            to_remote = self.expression2str(self.get_param("to_remote"))
            close_after_run = True if self.get_param("close_after_run") == "yes" else False
            sftp_put_file_key = self.get_param("sftp_put_file_key")

            ParamikoUtil.run_sftp_put(sftp_client, from_local, to_remote)
            self.populate_data(sftp_put_file_key, to_remote)

            if close_after_run:
                ParamikoUtil.close_sftp_client(sftp_client)
        else:
            logging.warning('sftp_client is not available, please use CREATE_SFTP_CLIENT task to setup.')
