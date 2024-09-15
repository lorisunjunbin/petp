import logging
import os
from threading import Condition

import wx

from core.definition.yamlro import YamlRO
from core.executionstate import ExecutionState
from core.loop import Loop
from core.processor import Processor
from core.task import Task
from mvp.presenter.event.PETPEvent import PETPEvent
from mvp.view.PETPView import PETPView
from utils.DateUtil import DateUtil
from utils.OSUtils import OSUtils

"""
Execution 1:n Task
"""


class Execution:
    """
    Execution class that contains a list of tasks and loops. This class is responsible for running the tasks in order.
    the instance could be serialized to yaml file and deserialized from yaml file.
    """

    def __init__(self, execution: str, list: list, loops: list = []):
        self.execution = execution
        self.list = list
        self.loops = loops

    def set_should_be_stop(self, stopOrNot: bool):
        """
        Call from outside to stop the execution
        """
        self.should_be_stop = stopOrNot

    def run(self, initial_data: dict, condition: Condition, view: PETPView) -> dict:
        data_chain = initial_data
        state: ExecutionState = ExecutionState(self.list)
        self.set_should_be_stop(False)

        if hasattr(self, 'loops'):
            self.loops.sort(key=lambda loop: loop.get_attribute('task_start'))

        while state.has_next():

            if self.should_be_stop:
                logging.info(f'Execution: [ {self.execution} ] is manually stop at task: {state.get_sequence()}')
                return data_chain

            current_loop: Loop = self.find_current_loop(state.get_sequence())
            state.init_loop(current_loop)

            if state.is_loop_start:
                state.setup_loop_start(data_chain)

            # process start -----
            task: Task = self.init_task(data_chain, state.get_current_index(), state.get_sequence())
            processor: Processor = self.init_processor(task, view, current_loop, state.is_loop_execution, condition)

            self.log_start_process(current_loop, state, processor, task, view)

            if hasattr(task, 'skipped') and task.skipped:
                self.log_skipped_process(current_loop, state, processor, task, view)
            else:
                # * main process *
                processor.do_process()

            task.end = DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")
            self.log_end_process(current_loop, state, processor, task, view)
            # process end ----

            if state.is_loop_end and state.setup_loop_end_then_continue(data_chain):
                continue

            state.move_to_next()

        return data_chain

    def post_log_reload(self, lp, view):
        if not lp.is_loop_execution:
            wx.PostEvent(view, PETPEvent(PETPEvent.LOG))

    def log_end_process(self, current_loop, loop_state, processor, task, view):
        logging.info(
            f'<-{task.end} <- {type(processor).__name__} <--------------< Task: {loop_state.get_sequence()} {(current_loop.get_loop_code() + "#" + str(loop_state.loop_times_cur)) if current_loop is not None else ""} Done \n')
        self.post_log_reload(loop_state, view)

    def log_start_process(self, current_loop, loop_state, processor, task, view):
        logging.info(
            f'>-{task.start} >- {type(processor).__name__} >---------------> Task: {loop_state.get_sequence()} {(current_loop.get_loop_code() + "#" + str(loop_state.loop_times_cur)) if current_loop is not None else ""}')
        logging.info(f'process start: {task.input}')
        self.post_log_reload(loop_state, view)

    def log_skipped_process(self, current_loop, loop_state, processor, task, view):
        logging.info(f'process *** skipped *** : {task.input}')
        self.post_log_reload(loop_state, view)

    def init_task(self, data_chain, idx, sequence) -> Task:
        task: Task = self.list[idx]
        task.data_chain = data_chain
        task.start = DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")
        task.run_sequence = sequence
        return task

    def init_processor(self, task, view, current_loop, is_loop_execution, condition) -> Processor:
        processor: Processor = Processor.get_processor_by_type(task.type)
        processor.set_execution(self)
        processor.set_task(task)
        processor.set_condition(condition)
        processor.set_view(view)
        processor.set_in_loop(is_loop_execution)
        processor.set_current_loop(current_loop)
        return processor

    def find_current_loop(self, sequence) -> Loop | None:
        if not hasattr(self, 'loops'):
            return None

        for loop in self.loops:
            if loop.get_task_start() <= sequence <= loop.get_task_end():
                loop.verify_loop()
                return loop

        return None

    def _get_file_path(self):
        return f'{os.path.realpath(".")}{os.sep}core{os.sep}executions{os.sep}{self.execution}.yaml'

    def delete(self):
        OSUtils.copy2(self._get_file_path(), os.path.realpath('core') + f'{os.sep}executions{os.sep}trash{os.sep}')
        OSUtils.delete_file_if_existed(self._get_file_path())

    def save(self):
        if len(self.list) > 0:
            YamlRO.write(self._get_file_path(), self)
            logging.info('Successfully save execution -> ' + self._get_file_path())

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def get_execution(filename):
        file_absolute_path = f'{os.path.realpath(".")}{os.sep}core{os.sep}executions{os.sep}{filename}.yaml'
        if OSUtils.is_file_existed(file_absolute_path):
            return YamlRO.get_yaml_from_file(file_absolute_path)
        else:
            logging.warning(f'File not existed: {file_absolute_path}')
            return None

    @staticmethod
    def get_available_executions():
        executions = OSUtils.get_file_list(os.path.realpath('core') + os.sep + 'executions')
        result = sorted([f.replace('.yaml', '') for f in executions if '.yaml' in f])
        return result
