import paramiko
import logging

from datetime import datetime


class ParamikoUtil:
    """
        # Esperanto: Paranoid + Friend

        pip install paramiko
    """

    @staticmethod
    def get_ssh_client(ip, uname, pwd):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, username=uname, password=pwd)
        logging.info(f'----- SSH - {ip} {uname}:*{pwd[1:3]}****----->')
        return ssh_client

    @staticmethod
    def close_ssh_client(ssh_client):
        ssh_client.close()
        logging.info('----- SSH - closed -----<')

    @staticmethod
    def run_ssh_cmd(ssh_client, cmd):
        logging.info('\nrun>' + cmd)

        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        stdout = stdout.readlines()

        output = []
        if (len(stdout) > 0):
            logging.info('------------------')
            for line in stdout:
                l = line.strip('\n')
                output.append(l)
                logging.info(l)

            for line in stderr:
                logging.info('E>>' + line.strip('\n'))
            logging.info('------------------\n')

        return output

    @staticmethod
    def get_sftp_client(ip, uname, pwd, port=22):
        transport = paramiko.Transport((ip, port))
        transport.connect(username=uname, password=pwd)
        sftp_client = paramiko.SFTPClient.from_transport(transport)
        logging.info(f'===== SFTP - {ip} {uname}:*{pwd[1:3]}***** =====>')
        return sftp_client

    @staticmethod
    def run_sftp_get(sftp_client, from_remote, to_local):
        logging.info(f'<{datetime.now()}> Start sftp GET from {from_remote} to {to_local}')
        sftp_client.get(remotepath=from_remote, localpath=to_local)
        logging.info(f'<{datetime.now()}> Done sftp GET from {from_remote} to {to_local}')

    @staticmethod
    def run_sftp_put(sftp_client, from_local, to_remote):
        logging.info(f'<{datetime.now()}> Start sftp PUT from {from_local} to {to_remote}')
        sftp_client.put(localpath=from_local, remotepath=to_remote)
        logging.info(f'<{datetime.now()}> Done sftp PUT from {from_local} to {to_remote} ')

    @staticmethod
    def close_sftp_client(sftp_client):
        sftp_client.close()
        logging.info('===== SFTP - closed =====<')
