import json
import logging
import os
import time
from datetime import datetime
from threading import Condition
from typing import TYPE_CHECKING, Any

try:
    import wx
except Exception:
    class _WxShim:
        @staticmethod
        def PostEvent(*args, **kwargs):
            return None

    wx = _WxShim()

from core.definition.yamlro import YamlRO
from core.executionstate import ExecutionState
from core.loop import Loop
from core.processor import Processor
from core.task import Task
from mvp.presenter.event.PETPEvent import PETPEvent
from utils.DateUtil import DateUtil
from utils.OSUtils import OSUtils

if TYPE_CHECKING:
    from mvp.view.PETPView import PETPView
else:
    PETPView = Any

"""
Execution 1:n Task
"""

_execution_cache: dict[str, tuple[float, Any]] = {}
_available_executions_cache: tuple[float, list] | None = None
_AVAILABLE_EXECUTIONS_TTL = 5.0


class Execution:
    """
    Execution class that contains a list of tasks and loops. This class is responsible for running the tasks in order.
    the instance could be serialized to yaml file and deserialized from yaml file.
    """

    def __init__(self, execution: str, list: list, mcp_desc: str, astool: bool = False, loops: list = None):
        self.execution = execution
        self.list = list
        self.loops = loops if loops is not None else []
        self.mcp_desc = mcp_desc
        self.astool = astool

    def set_should_be_stop(self, stopOrNot: bool):
        """
        Call from outside to stop the execution
        """
        self.should_be_stop = stopOrNot

    def init_run_at(self):
        self.run_at = datetime.now()

    def get_run_at(self) -> str:
        return self.run_at

    def run(self, initial_data: dict, condition: Condition, view: PETPView) -> dict:
        data_chain = initial_data
        mcp_defaults = self.expand_mcp_defaults(data_chain)
        for k, v in mcp_defaults.items():
            if k not in data_chain:
                data_chain[k] = v
        state: ExecutionState = ExecutionState(self.list)
        self.set_should_be_stop(False)
        self.init_run_at()
        self._last_log_post_time = 0.0  # throttle LOG events during loops

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

            proc_name = type(processor).__name__
            loop_cursor = self.collect_loop_cursor(current_loop, state)

            self.log_start_process(current_loop, state, processor, task, view, loop_cursor, proc_name)

            if hasattr(task, 'skipped') and task.skipped:
                self.log_skipped_process(current_loop, state, processor, task, view)
            else:
                # * main process *
                exception_policy = current_loop.get_exception_then() if current_loop else ''
                if exception_policy in ('continue', 'break'):
                    try:
                        processor.do_process()
                    except Exception as e:
                        logging.exception(
                            'Loop %s exception at task %s (policy=%s): %s',
                            current_loop.get_loop_code(), state.get_sequence(), exception_policy, e
                        )
                        task.end = DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")
                        self.log_end_process(current_loop, state, processor, task, view, loop_cursor, proc_name)
                        if exception_policy == 'continue':
                            if state.advance_loop_on_exception(data_chain):
                                continue
                            state.move_to_next()
                            continue
                        else:  # break
                            state.force_exit_loop(data_chain)
                            state.move_to_next()
                            continue
                else:
                    processor.do_process()

            task.end = DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")
            self.log_end_process(current_loop, state, processor, task, view, loop_cursor, proc_name)
            # process end ----

            # loop_condition: evaluate after every task inside a loop
            if state.is_loop_execution and current_loop:
                cond_action = self._eval_loop_condition(current_loop, data_chain)
                if cond_action == 'break':
                    state.force_exit_loop(data_chain)
                    state.move_to_next()
                    continue
                elif cond_action == 'continue':
                    if state.advance_loop_on_exception(data_chain):
                        continue
                    state.move_to_next()
                    continue

            if state.is_loop_end and state.setup_loop_end_then_continue(data_chain):
                continue

            goto_target = data_chain.pop('__goto_task', None)
            if goto_target is not None:
                idx = int(goto_target) - 1
                if 0 <= idx < len(self.list):
                    state.current_index = idx
                    logging.info('GO_TO_TASK: jumping to task %s', goto_target)
                    continue
                else:
                    logging.warning('GO_TO_TASK: target %s out of range (1-%s), ignoring', goto_target, len(self.list))

            state.move_to_next()

        return data_chain

    _LOOP_LOG_INTERVAL = 5  # seconds — minimum gap between LOG events during loops

    @staticmethod
    def _eval_loop_condition(current_loop: Loop, data_chain: dict):
        condition_body = current_loop.get_loop_condition()
        if not condition_body:
            return None
        from utils.CodeExplainerUtil import CodeExplainerUtil
        safe_code = current_loop.get_loop_code().replace('-', '_').replace(' ', '_')
        func_name = f'loop_condition_{safe_code}'
        cond_fn = CodeExplainerUtil.create_and_execute_func(
            func_name, '(data_chain)', condition_body)
        result = cond_fn(data_chain)
        triggered, action = result if isinstance(result, tuple) else (result, '')
        if triggered:
            logging.info('Loop %s condition triggered: %s', current_loop.get_loop_code(), action)
            return action if action in ('break', 'continue') else 'break'
        return None

    def post_log_reload(self, lp, view):
        evt_data = {"execution": self.execution, "task_index": lp.get_current_index()}
        if not lp.is_loop_execution:
            wx.PostEvent(view, PETPEvent(PETPEvent.LOG, data=evt_data))
        else:
            now = time.monotonic()
            if now - self._last_log_post_time >= self._LOOP_LOG_INTERVAL:
                self._last_log_post_time = now
                wx.PostEvent(view, PETPEvent(PETPEvent.LOG, data=evt_data))

    def log_end_process(self, current_loop, state, processor, task, view, loop_cursor=None, proc_name=None):
        if loop_cursor is None:
            loop_cursor = self.collect_loop_cursor(current_loop, state)
        if proc_name is None:
            proc_name = type(processor).__name__
        logging.info(
            '<-%s <- %s <--------------< Task: %s %s -- end << \n',
            task.end, proc_name, state.get_sequence(), loop_cursor)
        self.post_log_reload(state, view)

    def collect_loop_cursor(self, current_loop: Loop, state: ExecutionState) -> str:
        idx = "" if current_loop is None \
            else str(state.loop_times_cur) if state.is_times_loop \
            else str(state.current_loop_idx)
        loop_cursor = (current_loop.get_loop_code() + "@" + idx) if current_loop is not None else ""
        return loop_cursor

    def log_start_process(self, current_loop, state, processor, task, view, loop_cursor=None, proc_name=None):
        if loop_cursor is None:
            loop_cursor = self.collect_loop_cursor(current_loop, state)
        if proc_name is None:
            proc_name = type(processor).__name__
        logging.info(
            '>-%s >- %s >---------------> Task: %s %s -- begin >',
            task.start, proc_name, state.get_sequence(), loop_cursor)
        logging.info('process start: %s', task.input)
        self.post_log_reload(state, view)

    def log_skipped_process(self, current_loop, state, processor, task, view):
        logging.info('*** skipped *** : %s', task.input)
        self.post_log_reload(state, view)

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

    def get_mcp_input_defaults(self) -> dict:
        """Return raw default values from mcp_desc.inputSchema for executions marked as astool.

        Only applies when the first non-empty task is NOT INITIAL_PARAMS (i.e. defaults
        are not already covered by an explicit task). Returns an empty dict otherwise.
        """
        cached = getattr(self, '_mcp_input_defaults_cache', None)
        if cached is not None:
            return cached
        if not getattr(self, 'astool', False):
            return {}
        mcp_desc = getattr(self, 'mcp_desc', None)
        if not mcp_desc:
            return {}
        tasks = getattr(self, 'list', [])
        for task in tasks:
            if hasattr(task, 'type') and task.type.strip():
                if task.type.strip() == "INITIAL_PARAMS":
                    return {}
                break
        try:
            parsed = json.loads(mcp_desc)
        except (json.JSONDecodeError, TypeError):
            self._mcp_input_defaults_cache = {}
            return {}
        props = parsed.get("inputSchema", {}).get("properties", {})
        result = {name: spec["default"] for name, spec in props.items() if "default" in spec}
        self._mcp_input_defaults_cache = result
        return result

    def expand_mcp_defaults(self, data_chain: dict) -> dict:
        """Return MCP input defaults with expressions expanded using a Processor context.

        Creates a temporary Processor+Task so that expressions like {self.get_tdir()}
        are resolved through Processor.expression2str which has full context.
        """
        raw = self.get_mcp_input_defaults()
        if not raw:
            return {}
        tmp_task = Task(type="INITIAL_PARAMS", input="{}")
        tmp_task.data_chain = data_chain
        processor = Processor()
        processor.set_task(tmp_task)
        return {
            name: processor.expression2str(val) if isinstance(val, str) else val
            for name, val in raw.items()
        }

    def _get_file_path(self):
        return f'{os.path.realpath(".")}{os.sep}core{os.sep}executions{os.sep}{self.execution}.yaml'

    def delete(self):
        OSUtils.copy2(self._get_file_path(), os.path.realpath('core') + f'{os.sep}executions{os.sep}trash{os.sep}')
        OSUtils.delete_file_if_existed(self._get_file_path())
        _execution_cache.pop(self._get_file_path(), None)

    def save(self):
        if len(self.list) > 0:
            YamlRO.write(self._get_file_path(), self)
            _execution_cache.pop(self._get_file_path(), None)
            logging.info('Successfully save execution -> ' + self._get_file_path())

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def get_execution(filename):
        file_absolute_path = f'{os.path.realpath(".")}{os.sep}core{os.sep}executions{os.sep}{filename}.yaml'
        if not OSUtils.is_file_existed(file_absolute_path):
            logging.warning('File not existed: %s', file_absolute_path)
            return None
        mtime = os.path.getmtime(file_absolute_path)
        cached = _execution_cache.get(file_absolute_path)
        if cached is not None and cached[0] == mtime:
            return cached[1]
        result = YamlRO.get_yaml_from_file(file_absolute_path)
        _execution_cache[file_absolute_path] = (mtime, result)
        return result

    @staticmethod
    def invalidate_execution_cache(filename=None):
        if filename is None:
            _execution_cache.clear()
        else:
            file_absolute_path = f'{os.path.realpath(".")}{os.sep}core{os.sep}executions{os.sep}{filename}.yaml'
            _execution_cache.pop(file_absolute_path, None)

    @staticmethod
    def get_available_executions():
        global _available_executions_cache
        now = time.monotonic()
        if _available_executions_cache is not None:
            ts, result = _available_executions_cache
            if (now - ts) < _AVAILABLE_EXECUTIONS_TTL:
                return result
        executions = OSUtils.get_file_list(os.path.realpath('core') + os.sep + 'executions')
        result = sorted([f.replace('.yaml', '') for f in executions if '.yaml' in f])
        _available_executions_cache = (now, result)
        return result

    @staticmethod
    def get_tool_execution_names():
        """Return the set of execution names where astool is True."""
        tool_names = set()
        for name in Execution.get_available_executions():
            execution = Execution.get_execution(name)
            if execution and hasattr(execution, 'astool') and execution.astool:
                tool_names.add(name)
        return tool_names
