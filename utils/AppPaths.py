import os
import sys

_user_data_dir = None


def get_user_data_dir() -> str:
    global _user_data_dir
    if _user_data_dir is not None:
        return _user_data_dir

    if getattr(sys, 'frozen', False) and sys.platform == 'darwin':
        _user_data_dir = os.path.join(os.path.expanduser('~'), '.petp')
    else:
        _user_data_dir = os.path.realpath('.')
    return _user_data_dir


def get_executions_dir() -> str:
    return os.path.join(get_user_data_dir(), 'core', 'executions')


def get_pipelines_dir() -> str:
    return os.path.join(get_user_data_dir(), 'core', 'pipelines')


def get_config_dir() -> str:
    return os.path.join(get_user_data_dir(), 'config')


def get_log_dir() -> str:
    return os.path.join(get_user_data_dir(), 'log')


def get_download_dir() -> str:
    return os.path.join(get_user_data_dir(), 'download')
