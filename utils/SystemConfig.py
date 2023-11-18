import logging
import os

import yaml


class SystemConfig():

    def __init__(self, fileName):

        self.config_path = os.path.realpath('config') + fileName
        logging.debug('load config file from: ' + self.config_path)

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
            yaml.dump(self.yamldoc, f, default_flow_style=False)
        logging.debug('set_config -' + str(keys) + '= ' + value)

    def bind_model(self, model, keys=[], excludeKeys=[]):
        for idx, key in enumerate(keys):
            configSet = self.yamldoc[key]
            for k, v in configSet.items():
                if k not in excludeKeys:
                    setattr(model, k, v)
                    logging.info(f'bindmodel: {key}  [ {k} = {v} ]')
