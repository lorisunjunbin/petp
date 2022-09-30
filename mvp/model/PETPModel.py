import logging

from utils import SystemConfig


class PETPModel(object):

    def __init__(self, config: SystemConfig):
        # refer to: config/petpconfig.yaml
        self.sysconfig = config
        self.sysconfig.bind_model(self, ['application'])
        logging.info('Init PETPModel')

    def set_config(self, key, value):
        self.sysconfig.set_config(value, 'application', key)

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
