import json
import logging
import os

from core.cron.runnableascron import RunnAbleAsCron
from core.definition.yamlro import YamlRO
from core.execution import Execution
from utils.DateUtil import DateUtil
from utils.OSUtils import OSUtils

"""
Pipeline 1-n Execution
"""


class Pipeline(RunnAbleAsCron):
    pipeline: str
    cronExp: str
    cronEnabled: bool
    list: list  # item of list: {execution:'', input:''}

    def __init__(self, pipeline, list, cronEnabled=False, cronExp='0 * * * *'):

        self.pipeline = pipeline
        self.cronExp = cronExp
        self.cronEnabled = cronEnabled
        self.list = list

    async def run(self, initdata={}):
        self._run(initdata)

    def runsync(self, initdata={}):
        self._run(initdata)

    def get_name(self):
        return self.pipeline

    def get_key(self):
        return f'{self.pipeline}_{self.cronExp}'

    def get_cron(self):
        return self.cronExp

    def _run(self, initdata={}):

        data_chain = initdata | {'run_in_pipeline': 'yes'}

        logging.info(f'<<<<<<<<<<<<<<<<<<<<<-  Start RUN Pipeline: {self.pipeline} - >>>>>>>>>>>>>>>>>>>>>')

        for idx, executionDic in enumerate(self.list, start=1):
            executionInitData: dict = self.load_proper_input(executionDic)

            data_chain = executionInitData | data_chain

            execution: Execution = Execution.get_execution(executionDic['execution'])

            logging.info(
                f'[ {self.pipeline} ]>>{DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")} >============> Execution {idx}: {execution.execution}')

            data_chain = execution.run_sync(data_chain)

            logging.info(
                f'[ {self.pipeline} ]<<{DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")} <============< Execution {idx}: {execution.execution} < DONE \n')

        logging.info(f'<<<<<<<<<<<<<<<<<<<<<-  Successfully RUN Pipeline: {self.pipeline} - >>>>>>>>>>>>>>>>>>>>>')

    def load_proper_input(self, executionDic):
        try:
            result = json.loads(executionDic['input'])
            if type(result) is dict:
                return result
            logging.warning(f"invalid input {executionDic['input']} for execution: {executionDic['execution']}, will return empty dict.")
            return {}
        except:
            logging.warning(f"invalid input {executionDic['input']} for execution: {executionDic['execution']}, will return empty dict.")
            return {}

    def _get_file_path(self):
        return f'{os.path.realpath(".")}/core/pipelines/{self.pipeline}.yaml'

    def delete(self):
        fp = self._get_file_path()
        OSUtils.copy2(fp, os.path.realpath('core') + '/pipelines/trash/')
        OSUtils.delete_file_if_existed(fp)

    def save(self):
        if (len(self.list) > 0):
            YamlRO.write(self._get_file_path(), self)
            logging.info('Successfully save cron -> ' + self._get_file_path())

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def get_pipeline(filename):
        file_absolute_path = f'{os.path.realpath(".")}/core/pipelines/{filename}.yaml'
        if OSUtils.is_file_existed(file_absolute_path):
            # logging.info(f'Load pipeline from {file_absolute_path}')
            return YamlRO.get_yaml_from_file(file_absolute_path)
        else:
            logging.warning(f'File not existed: {file_absolute_path}')
            return None

    @staticmethod
    def get_available_pipelines():
        pipelines = OSUtils.get_file_list(os.path.realpath('core') + '/pipelines')
        result = list(map(lambda f: f.replace('.yaml', ''), pipelines))
        result.sort()

        return result
