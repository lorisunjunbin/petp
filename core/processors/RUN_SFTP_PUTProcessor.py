import logging

from paramiko.sftp_client import SFTPClient

from core.processor import Processor
from utils.ParamikoUtil import ParamikoUtil


class RUN_SFTP_PUTProcessor(Processor):
    TPL: str = '{"from_local":"","to_remote": "","sftp_client_key":"sftpclient", "sftp_put_file_key":"", "close_after_run":"yes|no"}'
    DESC: str = f''' 

        Put file from [from_local] to [to_remote], via paramiko require [sftp_client_key] of data_chain. 
        Save target location to [sftp_put_file_key] of data_chain.
        Able to close sftp client by [close_after_run]

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
