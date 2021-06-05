import logging
import os

import yaml


class SystemConfig():

    def __init__(self, fileName):

        self.config_path = os.path.realpath('config') + fileName
        logging.info('load config file from: ' + self.config_path)

        with open(self.config_path, 'r', encoding='utf8') as f:
            self.yamldoc = yaml.safe_load(f)

    def get_config(self, *keys):
        try:
            result = self.yamldoc

            for key in keys:
                result = result[key]

            logging.info('get_config -' + str(keys) + '= ' + result)
            return result
        except Exception as e:
            logging.warning("get_config - " + str(keys) + ' is None')
            return None

    def set_config(self, value, *keys):
        logging.info('set_config - update configs: ' + str(keys) + '->' + value)

        if (len(keys) == 1):
            self.yamldoc[keys[0]] = value
        elif (len(keys) == 2):
            self.yamldoc[keys[0]][keys[1]] = value
        elif (len(keys) == 3):
            self.yamldoc[keys[0]][keys[1]][keys[2]] = value
        else:
            raise KeyError('invalid keys !')

        with open(self.config_path, 'w', encoding='utf8') as f:
            yaml.dump(self.yamldoc, f, default_flow_style=False)

        logging.info('set_config - save config file to: ' + self.config_path)

    def bind_model(self, model, keys=[], excludeKeys=[]):
        for idx, key in enumerate(keys):
            configSet = self.yamldoc[key]
            for k, v in configSet.items():
                if k not in excludeKeys:
                    setattr(model, k, v)
                    logging.info(f'bindmodel: {key}  [ {k} = {v} ]')
