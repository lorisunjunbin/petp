import os
import sys
import logging
import time
from os import listdir
from os.path import isfile, join
from shutil import copy2, copyfile


class OSUtils:

    @staticmethod
    def get_sytem():
        """
        AIX  -> 'aix'
        Linux -> 'linux'
        Windows -> 'win32'
        Windows/Cygwin -> 'cygwin'
        macOS -> 'darwin'
        """
        return sys.platform

    @staticmethod
    def wait_for_file_within_seconds(file_path, timeout):
        logging.info(f'waiting {timeout} seconds for file:{file_path}')
        wait = 0
        while not os.path.exists(file_path) and wait < timeout:
            time.sleep(1)
            wait += 1
        if os.path.isfile(file_path):
            logging.info(f'Found after {wait} seconds for file:{file_path}')
            return True
        else:
            logging.warning(f'Not found after {timeout} seconds for file:{file_path}')
            return False

    @staticmethod
    def wait_for_folder_reach_expectcount_within_seconds(source_folder, expect_count, timeout):
        logging.info(f'waiting {timeout} seconds for file:{source_folder}')
        wait = 0
        while len(OSUtils.get_file_list(source_folder)) < expect_count and wait < timeout:
            time.sleep(1)
            wait += 1

        source_files = OSUtils.get_file_list(source_folder)
        result = len(source_files)
        logging.info(f" {result} file(s) downloaded , {str(source_files)}")
        return result

    @staticmethod
    def get_file_list(file_path):
        return [f for f in listdir(file_path) if isfile(join(file_path, f)) and not f.startswith('.') and not f.endswith('.crdownload')]

    @staticmethod
    def is_file_existed(file_path):
        return os.path.exists(file_path)

    @staticmethod
    def get_root_folder():
        return os.path.realpath('.')

    @staticmethod
    def get_file_collected_folder():
        return os.path.realpath('file_collected')

    @staticmethod
    def get_download_folder():
        return os.path.realpath('download')

    @staticmethod
    def get_ewa_folder():
        return os.path.realpath('folder_file')

    @staticmethod
    def delete_file_if_existed(file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f'deleted existing file: {file_path}')

    @staticmethod
    def copy_file(source, target):
        copyfile(source, target)
        logging.info(f'copy_file {source} -> {target} ')

    @staticmethod
    def copy2(source, target):
        copy2(source, target)
        logging.info(f'copy2 {source} -> {target} ')

    @staticmethod
    def create_folder(folder):
        os.makedirs(folder)
        logging.info(f'create_folder {folder}')

    @staticmethod
    def create_folder_if_not_existed(filePath):
        os.makedirs(filePath, exist_ok=True)

    @staticmethod
    def get_log_file_path(app) -> str:
        log_folder = os.path.realpath('log')
        OSUtils.create_folder_if_not_existed(log_folder)
        return f'{log_folder}/{app}.log'
