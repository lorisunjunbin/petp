import os
from os import listdir
from os.path import isfile, join
from shutil import copy2, copyfile


class Utils:

    @staticmethod
    def get_file_list(file_path):
        return [f for f in listdir(file_path) if isfile(join(file_path, f))]

    @staticmethod
    def get_file_list_without_tmp(file_path):
        return [f for f in listdir(file_path) if isfile(join(file_path, f))
                and not f.startswith('.')
                and not f.endswith('.crdownload')
                and not f.endswith('.tmp')
                ]

    @staticmethod
    def is_file_existed(file_path):
        return os.path.exists(file_path)

    @staticmethod
    def get_root_folder():
        return os.path.realpath('.')

    @staticmethod
    def delete_file_if_existed(file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

    @staticmethod
    def copy_file(source, target):
        copyfile(source, target)

    @staticmethod
    def copy2(source, target):
        copy2(source, target)

    @staticmethod
    def create_folder(folder):
        os.makedirs(folder)

    @staticmethod
    def create_folder_if_not_existed(filePath):
        os.makedirs(filePath, exist_ok=True)

    @staticmethod
    def collect_files(start_path, depth_lambda=lambda depth: True, file_name_lambda=lambda file_name: True):
        result = []
        for current_folder, sub_dirs, files in os.walk(start_path):
            current_rel_folder = current_folder.replace(start_path, '')
            depth = current_rel_folder.count(os.sep)
            if depth_lambda(depth):
                for file_name in files:
                    rel_file = os.path.join(current_rel_folder, file_name)
                    if file_name_lambda(rel_file):
                        result.append(rel_file)

        return result
