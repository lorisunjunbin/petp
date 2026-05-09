import logging
import os

import yaml

from utils.AppPaths import get_config_dir


class SystemConfig():

    def __init__(self, file_name):
        self.config_path = os.path.join(get_config_dir(), file_name)
        logging.info(f'load config file from: {self.config_path}')

        with open(self.config_path, 'r', encoding='utf8') as f:
            self.yamldoc = yaml.safe_load(f)

    def get_config(self, *keys):
        try:
            result = self.yamldoc
            for key in keys:
                result = result[key]
            logging.debug('get_config -' + str(keys) + '= ' + result)
            return result
        except Exception as e:
            logging.warning("get_config - " + str(keys) + ' is None')
            return None

    def set_config(self, value, *keys):
        temp = self.yamldoc
        for key in keys[:-1]:
            temp = temp[key]
        temp[keys[-1]] = value
        with open(self.config_path, 'w', encoding='utf8') as f:
            yaml.dump(self.yamldoc, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        logging.debug('set_config -' + str(keys) + '= ' + str(value))

    def bind_model(self, model, keys=None, exclude_keys=None):
        if keys is None:
            keys = []
        if exclude_keys is None:
            exclude_keys = []
        for idx, key in enumerate(keys):
            config_set = self.yamldoc[key]
            for k, v in config_set.items():
                if k not in exclude_keys:
                    setattr(model, k, v)
                    logging.info(f'bindmodel: {key}  [ {k} = {v} ]')
