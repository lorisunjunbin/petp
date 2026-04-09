import paramiko
import logging

from datetime import datetime
from typing import List, Tuple
from paramiko.client import SSHClient
from paramiko.sftp_client import SFTPClient


class ParamikoUtil:
    """
        # Esperanto: Paranoid + Friend

        pip install paramiko
    """

    # ─── helpers ───

    @staticmethod
    def _mask_pwd(pwd: str) -> str:
        """Safely mask password for logging."""
        if not pwd:
            return '***'
        return f'*{"" if len(pwd) < 3 else pwd[1:3]}****'

    # ─── SSH ───

    @staticmethod
    def get_ssh_client(ip: str, uname: str, pwd: str, port: int = 22) -> SSHClient:
        """Create and return an SSH client connected to the given host."""
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, port=port, username=uname, password=pwd)
            logging.info(f'----- SSH - {ip}:{port} {uname}:{ParamikoUtil._mask_pwd(pwd)} ----->')
            return ssh_client
        except Exception as e:
            logging.error(f'Failed to create SSH client to {ip}:{port} - {e}')
            raise

    @staticmethod
    def close_ssh_client(ssh_client: SSHClient) -> None:
        """Close an SSH client safely."""
        try:
            ssh_client.close()
            logging.info('----- SSH - closed -----<')
        except Exception as e:
            logging.warning(f'Error closing SSH client: {e}')

    @staticmethod
    def run_ssh_cmd(ssh_client: SSHClient, cmd: str) -> List[str]:
        """
        Execute a command over SSH and return stdout lines.
        stderr is always logged separately.
        """
        logging.info(f'\nrun> {cmd}')
        try:
            _, stdout_ch, stderr_ch = ssh_client.exec_command(cmd)
            stdout_lines = stdout_ch.readlines()
            stderr_lines = stderr_ch.readlines()

            output = [line.strip('\n') for line in stdout_lines]
            errors = [line.strip('\n') for line in stderr_lines]

            logging.info('------------------')
            for line in output:
                logging.info(line)
            for line in errors:
                logging.warning(f'E>> {line}')
            logging.info('------------------\n')

            return output
        except Exception as e:
            logging.error(f'Failed to run SSH command "{cmd}": {e}')
            raise

    @staticmethod
    def run_ssh_cmd_full(ssh_client: SSHClient, cmd: str) -> Tuple[List[str], List[str], int]:
        """
        Execute a command over SSH and return (stdout_lines, stderr_lines, exit_code).
        """
        logging.info(f'\nrun> {cmd}')
        try:
            _, stdout_ch, stderr_ch = ssh_client.exec_command(cmd)

            stdout_lines = [line.strip('\n') for line in stdout_ch.readlines()]
            stderr_lines = [line.strip('\n') for line in stderr_ch.readlines()]
            exit_code = stdout_ch.channel.recv_exit_status()

            logging.info('------------------')
            for line in stdout_lines:
                logging.info(line)
            for line in stderr_lines:
                logging.warning(f'E>> {line}')
            logging.info(f'exit_code: {exit_code}')
            logging.info('------------------\n')

            return stdout_lines, stderr_lines, exit_code
        except Exception as e:
            logging.error(f'Failed to run SSH command "{cmd}": {e}')
            raise

    # ─── SFTP ───

    @staticmethod
    def get_sftp_client(ip: str, uname: str, pwd: str, port: int = 22) -> SFTPClient:
        """
        Create and return an SFTP client via Transport.
        The Transport is stored on the client so it can be closed properly later.
        """
        try:
            transport = paramiko.Transport((ip, port))
            transport.connect(username=uname, password=pwd)
            sftp_client = paramiko.SFTPClient.from_transport(transport)
            if sftp_client is None:
                transport.close()
                raise ConnectionError(f'Failed to create SFTP session to {ip}:{port}')
            # keep a reference so close_sftp_client can also close the transport
            sftp_client._petp_transport = transport
            logging.info(f'===== SFTP - {ip}:{port} {uname}:{ParamikoUtil._mask_pwd(pwd)} =====>')
            return sftp_client
        except Exception as e:
            logging.error(f'Failed to create SFTP client to {ip}:{port} - {e}')
            raise

    @staticmethod
    def get_sftp_from_ssh(ssh_client: SSHClient) -> SFTPClient:
        """Open an SFTP session directly from an existing SSH client (no extra Transport)."""
        try:
            sftp_client = ssh_client.open_sftp()
            logging.info('===== SFTP (via SSH) opened =====>')
            return sftp_client
        except Exception as e:
            logging.error(f'Failed to open SFTP from SSH client: {e}')
            raise

    @staticmethod
    def run_sftp_get(sftp_client: SFTPClient, from_remote: str, to_local: str) -> None:
        """Download a file from remote to local."""
        logging.info(f'<{datetime.now()}> Start sftp GET from {from_remote} to {to_local}')
        try:
            sftp_client.get(remotepath=from_remote, localpath=to_local)
            logging.info(f'<{datetime.now()}> Done sftp GET from {from_remote} to {to_local}')
        except Exception as e:
            logging.error(f'sftp GET failed ({from_remote} -> {to_local}): {e}')
            raise

    @staticmethod
    def run_sftp_put(sftp_client: SFTPClient, from_local: str, to_remote: str) -> None:
        """Upload a file from local to remote."""
        logging.info(f'<{datetime.now()}> Start sftp PUT from {from_local} to {to_remote}')
        try:
            sftp_client.put(localpath=from_local, remotepath=to_remote)
            logging.info(f'<{datetime.now()}> Done sftp PUT from {from_local} to {to_remote}')
        except Exception as e:
            logging.error(f'sftp PUT failed ({from_local} -> {to_remote}): {e}')
            raise

    @staticmethod
    def run_sftp_listdir(sftp_client: SFTPClient, remote_path: str = '.') -> List[str]:
        """List files in a remote directory."""
        try:
            entries = sftp_client.listdir(remote_path)
            logging.info(f'sftp LISTDIR {remote_path}: {len(entries)} entries')
            return entries
        except Exception as e:
            logging.error(f'sftp LISTDIR failed ({remote_path}): {e}')
            raise

    @staticmethod
    def close_sftp_client(sftp_client: SFTPClient) -> None:
        """Close SFTP client and its underlying Transport (if created by get_sftp_client)."""
        try:
            sftp_client.close()
            # also close the transport we saved during creation
            transport = getattr(sftp_client, '_petp_transport', None)
            if transport:
                transport.close()
            logging.info('===== SFTP - closed =====<')
        except Exception as e:
            logging.warning(f'Error closing SFTP client: {e}')
