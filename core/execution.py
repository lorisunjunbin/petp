import logging
import os

from core.definition.yamlro import YamlRO
from core.processor import Processor
from utils.DateUtil import DateUtil
from utils.OSUtils import OSUtils

"""
Execution 1:n Task
"""


class Execution(object):
    execution: str
    list: list

    def __init__(self, execution, lt):
        self.execution = execution
        self.list = lt

    async def run(self, initial_data) -> dict:
        return self._run(initial_data)

    def run_sync(self, initial_data) -> dict:
        return self._run(initial_data)

    def _run(self, initial_data):

        data_chain = initial_data

        for idx, task in enumerate(self.list, start=1):
            task.data_chain = data_chain
            task.start = DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")
            task.run_sequence = idx

            processor: Processor = Processor.get_processor_by_type(task.type)
            processor.set_task(task)

            logging.info(f'>-{task.start} >- {type(processor).__name__} -----------------------> Task: {idx}')
            logging.info(f'process task start: {task.input} - {str(task.data_chain)}')

            processor.do_process()

            task.end = DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")

            logging.info(f'process task done: {str(task)}')
            logging.info(f'<-{task.end} <- {type(processor).__name__} -----------------------< Task: {idx} Done \n')

        return data_chain

    def _get_file_path(self):
        return f'{os.path.realpath(".")}/core/executions/{self.execution}.yaml'

    def delete(self):
        OSUtils.copy2(self._get_file_path(), os.path.realpath('core') + '/executions/trash/')
        OSUtils.delete_file_if_existed(self._get_file_path())

    def save(self):
        if len(self.list) > 0:
            YamlRO.write(self._get_file_path(), self)
            logging.info('Successfully save execution -> ' + self._get_file_path())

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def get_execution(filename):
        file_absolute_path = f'{os.path.realpath(".")}/core/executions/{filename}.yaml'
        if OSUtils.is_file_existed(file_absolute_path):
            # logging.info(f'Load execution from {file_absolute_path}')
            return YamlRO.get_yaml_from_file(file_absolute_path)
        else:
            logging.warning(f'File not existed: {file_absolute_path}')
            return None

    @staticmethod
    def get_available_executions():
        executions = OSUtils.get_file_list(os.path.realpath('core') + '/executions')
        result = list(map(lambda f: f.replace('.yaml', ''), executions))
        result.sort()

        return result
