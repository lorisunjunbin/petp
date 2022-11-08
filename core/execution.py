import logging
import os

from core.definition.yamlro import YamlRO
from core.loop import Loop
from core.processor import Processor
from core.task import Task
from utils.DateUtil import DateUtil
from utils.OSUtils import OSUtils

"""
Execution 1:n Task
"""


class Execution(object):
    execution: str
    list: list
    loops: []
    should_be_stop: bool

    def __init__(self, execution, lt, lps):
        self.execution = execution
        self.list = lt
        self.loops = lps

    def run(self, initial_data) -> dict:
        data_chain = initial_data
        list_size = len(self.list)
        # loop for collection
        current_loop_collection: []
        current_loop_idx = 0

        # loop for times
        loop_times = 0
        loop_times_cur = 0
        self.should_be_stop = False

        if hasattr(self, 'loops'):
            self.loops.sort(key=lambda loop: loop.get_attribute('task_start'))

        idx = 0
        while idx < list_size:

            sequence: int = idx + 1

            if self.should_be_stop:
                logging.info(f'Execution: [ {self.execution} ] is manually stop at task: {sequence}')
                return data_chain

            current_loop: Loop = self.find_current_loop(sequence)
            is_loop_execution: bool = current_loop is not None
            is_times_loop: bool = is_loop_execution and current_loop.is_loop_for_times()
            is_loop_start: bool = is_loop_execution and sequence == current_loop.get_task_start()
            is_loop_end: bool = is_loop_execution and sequence == current_loop.get_task_end()

            if is_loop_start:
                if is_times_loop:
                    loop_times = current_loop.get_loop_times()
                    data_chain[current_loop.get_loop_index_key()] = loop_times_cur
                else:  # is_collection_loop
                    current_loop_collection = data_chain[current_loop.get_loop_key()]
                    if len(current_loop_collection) > current_loop_idx:
                        data_chain[current_loop.get_item_key()] = current_loop_collection[current_loop_idx]
                        data_chain[current_loop.get_loop_index_key()] = current_loop_idx

            # process start -----
            task: Task = self.list[idx]
            task.data_chain = data_chain
            task.start = DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")
            task.run_sequence = sequence

            processor: Processor = Processor.get_processor_by_type(task.type)
            processor.set_task(task)

            logging.info(f'>-{task.start} >- {type(processor).__name__} >---------------> Task: {sequence} {(current_loop.get_loop_code() + "#" + str(loop_times_cur)) if current_loop is not None else ""}')
            logging.info(f'process start: {task.input}')

            processor.do_process()

            task.end = DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")
            logging.info(f'<-{task.end} <- {type(processor).__name__} <--------------< Task: {sequence} {(current_loop.get_loop_code() + "#" + str(loop_times_cur)) if current_loop is not None else ""} Done \n')
            # process end ----

            if is_loop_end:
                if is_times_loop:
                    loop_times_cur += 1
                    if loop_times > loop_times_cur:
                        idx = current_loop.get_task_start() - 1
                        data_chain[current_loop.get_loop_index_key()] = loop_times_cur
                        continue
                    else:  # is_collection_loop
                        loop_times_cur = 0
                        loop_times = 0
                        data_chain[current_loop.get_loop_index_key()] = 0
                else:
                    current_loop_idx += 1
                    if len(current_loop_collection) > current_loop_idx:
                        idx = current_loop.get_task_start() - 1
                        data_chain[current_loop.get_loop_index_key()] = current_loop_idx
                        continue
                    else:
                        current_loop_idx = 0
                        data_chain[current_loop.get_item_key()] = None
                        data_chain[current_loop.get_loop_index_key()] = 0

            idx += 1

        return data_chain

    def find_current_loop(self, sequence):
        if not hasattr(self, 'loops'):
            return None

        for loop in self.loops:
            if loop.get_task_start() <= sequence <= loop.get_task_end():
                loop.verify_loop()
                return loop
            else:
                return None

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
