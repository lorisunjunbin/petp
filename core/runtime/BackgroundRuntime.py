import json
import logging
import time
import threading
from queue import SimpleQueue
from threading import Condition
from typing import Any, Optional

from core.cron.cron import Cron
from core.cron.cron_history import CronHistory
from core.execution import Execution
from core.executionstate import ExecutionState
from core.pipeline import Pipeline
from core.processor import Processor
from core.runtime.UiProcessorPolicy import decide
from core.task import Task
from httpservice.constants import HTTP_RESPONSE_KEY
from utils.DateUtil import DateUtil


class BackgroundRuntime:
    _TOOLS_CACHE_TTL = 60

    def __init__(self, model: Any, ui_policy: str = "skip"):
        self.model = model
        self.ui_policy = ui_policy
        self._tools_cache: dict | None = None
        self._tools_cache_ts: float = 0.0
        self._cron: Cron | None = None
        self._running_pipelines: set[str] = set()
        self._running_pipelines_lock = threading.Lock()
        max_records = getattr(model, 'cron_history_max_records', 500) if model else 500
        self._cron_history = CronHistory(max_records=max_records)
        from core.execution import set_static_mode
        set_static_mode(True)

    def run_execution(self, execution_name: str, init_data: Optional[dict] = None,
                       progress_queue: Optional[SimpleQueue] = None) -> dict:
        started = time.time()
        execution = Execution.get_execution(execution_name)
        if execution is None:
            return self._result(False, {}, f"Execution not found: {execution_name}", started)

        data_chain = dict(init_data or {})
        mcp_defaults = execution.expand_mcp_defaults(data_chain)
        for k, v in mcp_defaults.items():
            if k not in data_chain:
                data_chain[k] = v
        data_chain.update({"__m": self.model, "__p": self})
        cond = Condition()
        skipped_tasks = []

        state = ExecutionState(execution.list)
        total = len(execution.list)
        execution.set_should_be_stop(False)
        execution.init_run_at()
        if hasattr(execution, "loops"):
            execution.loops.sort(key=lambda loop: loop.get_attribute("task_start"))

        try:
            while state.has_next():
                if getattr(execution, "should_be_stop", False):
                    logging.info(
                        "Execution: [ %s ] is manually stop at task: %s",
                        execution_name,
                        state.get_sequence(),
                    )
                    break

                seq = state.get_sequence()
                task: Task = execution.list[state.get_current_index()]

                current_loop = execution.find_current_loop(seq)
                state.init_loop(current_loop)
                if state.is_loop_start:
                    state.setup_loop_start(data_chain)

                task.data_chain = data_chain
                task.run_sequence = seq
                task.start = DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")

                processor = Processor.get_processor_by_type(task.type)
                processor.set_execution(execution)
                processor.set_task(task)
                processor.set_condition(cond)
                processor.set_view(None)
                processor.set_in_loop(state.is_loop_execution)
                processor.set_current_loop(current_loop)

                proc_name = type(processor).__name__
                loop_cursor = self._collect_loop_cursor(current_loop, state)

                skip_range = data_chain.get('__skip_range')
                if not hasattr(task, '_orig_skipped'):
                    task._orig_skipped = getattr(task, 'skipped', False)
                else:
                    task.skipped = task._orig_skipped
                if skip_range and skip_range[0] <= seq <= skip_range[1]:
                    task.skipped = True
                if skip_range and seq > skip_range[1]:
                    data_chain.pop('__skip_range', None)

                self._log_start_process(seq, proc_name, loop_cursor, task)
                _task_start_ts = time.time()
                if progress_queue is not None:
                    progress_queue.put(f"[{seq}/{total}] {task.type} started")

                skip_reason = self._skip_reason(task)
                if skip_reason is not None:
                    skipped_tasks.append({"task_index": seq, "task_type": task.type, "reason": skip_reason})
                    self._log_skipped_process(task)
                    logging.info(
                        "Skip task @execution=%s task=%s type=%s reason=%s",
                        execution_name,
                        seq,
                        task.type,
                        skip_reason,
                    )
                else:
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
                            self._log_end_process(seq, proc_name, loop_cursor, task)
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
                self._log_end_process(seq, proc_name, loop_cursor, task)
                if progress_queue is not None:
                    duration_ms = int((time.time() - _task_start_ts) * 1000)
                    progress_queue.put(f"[{seq}/{total}] {task.type} done ({duration_ms}ms)")

                # loop_condition: evaluate after every task inside a loop
                if state.is_loop_execution and current_loop:
                    cond_action = Execution._eval_loop_condition(current_loop, data_chain)
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
                    if 0 <= idx < len(execution.list):
                        state.current_index = idx
                        logging.info('GO_TO_TASK: jumping to task %s', goto_target)
                        continue
                    else:
                        logging.warning('GO_TO_TASK: target %s out of range (1-%s), ignoring', goto_target, len(execution.list))

                if data_chain.pop('__end_execution', None):
                    logging.info('END_EXECUTION: early termination signaled')
                    break

                state.move_to_next()
        except Exception as e:
            logging.exception("Execution failed: %s", execution_name)
            return self._result(
                False,
                data_chain,
                f"Execution failed: {execution_name}, error: {e}",
                started,
                skipped_tasks,
            )

        return self._result(True, data_chain, None, started, skipped_tasks)

    def run_pipeline(self, pipeline_name: str, init_data: Optional[dict] = None) -> dict:
        started = time.time()
        pipeline = Pipeline.get_pipeline(pipeline_name)
        if pipeline is None:
            return self._result(False, {}, f"Pipeline not found: {pipeline_name}", started)

        if getattr(pipeline, 'cronEnabled', False):
            return self._run_pipeline_as_cron(pipeline, started)

        with self._running_pipelines_lock:
            if pipeline_name in self._running_pipelines:
                return self._result(False, {}, f"Pipeline already running: {pipeline_name}", started)
            self._running_pipelines.add(pipeline_name)

        try:
            return self._run_pipeline_once(pipeline, pipeline_name, init_data, started)
        finally:
            with self._running_pipelines_lock:
                self._running_pipelines.discard(pipeline_name)

    def _run_pipeline_as_cron(self, pipeline: Pipeline, started: float) -> dict:
        cron_exp = getattr(pipeline, 'cronExp', '')
        cron_desc = getattr(pipeline, 'cronDesc', '')
        if self._cron is None:
            self._cron = Cron(None, on_run=self._cron_run_pipeline)
        self._cron.add_one(pipeline)
        logging.info('Pipeline %s registered as cron [ %s ] %s', pipeline.pipeline, cron_exp, cron_desc)
        return self._result(True, {}, None, started, [], {
            "mode": "cron",
            "cronExp": cron_exp,
            "cronDesc": cron_desc,
        })

    def stop_pipeline_cron(self, pipeline_name: str) -> None:
        if self._cron is None:
            return
        pipeline = Pipeline.get_pipeline(pipeline_name)
        if pipeline is not None:
            self._cron.stop_one(pipeline)

    def stop_all_cron(self) -> None:
        if self._cron is not None:
            self._cron.stop_all()

    def get_active_crons(self) -> list[dict]:
        if self._cron is None:
            return []
        return self._cron.get_running_info()

    def get_cron_history(self, pipeline_name: Optional[str] = None, limit: int = 50) -> list[dict]:
        return self._cron_history.get_history(pipeline_name, limit)

    def get_cron_record(self, record_id: str) -> Optional[dict]:
        return self._cron_history.get_record(record_id)

    def _cron_run_pipeline(self, cron_obj, init_data: dict) -> None:
        pipeline_name = cron_obj.get_name()
        started = time.time()
        result = self._run_pipeline_once(cron_obj, pipeline_name, init_data, started)
        logging.info("Cron pipeline result: %s", json.dumps(result, ensure_ascii=False, default=str))
        self._cron_history.record(pipeline_name, getattr(cron_obj, 'cronExp', ''), result)

    def _run_pipeline_once(self, pipeline: Pipeline, pipeline_name: str, init_data: Optional[dict], started: float) -> dict:
        cron_desc = getattr(pipeline, 'cronDesc', '')
        cron_exp = getattr(pipeline, 'cronExp', '')
        logging.info('<<<<<<<<<<<<<<<<<<<<<-  Start RUN Pipeline: %s  [ %s ] %s - >>>>>>>>>>>>>>>>>>>>>', pipeline_name, cron_exp, cron_desc)

        data_chain = dict(init_data or {})
        data_chain['run_in_pipeline'] = 'yes'
        total_steps = len(pipeline.list)
        execution_results = []

        try:
            for idx, execution_def in enumerate(pipeline.list, start=1):
                execution_name = execution_def.get("execution")
                execution_input = pipeline.load_proper_input(execution_def)
                merged_input = dict(data_chain)
                merged_input.update(execution_input)
                merged_input['__pipeline_context'] = {
                    'pipeline_name': pipeline_name,
                    'step_index': idx - 1,
                    'step_total': total_steps,
                    'is_pipeline': True,
                }

                logging.info('[ %s ]>> Execution %s: %s', pipeline_name, idx, execution_name)

                result = self.run_execution(execution_name, merged_input)
                execution_results.append({"execution": execution_name, "result": result})

                logging.info('[ %s ]<< Execution %s: %s < %s', pipeline_name, idx, execution_name, 'DONE' if result["ok"] else 'FAILED')

                if not result["ok"]:
                    logging.info('<<<<<<<<<<<<<<<<<<<<<-  FAILED RUN Pipeline: %s - >>>>>>>>>>>>>>>>>>>>>', pipeline_name)
                    return self._result(
                        False,
                        result.get("data", {}),
                        f"Pipeline failed at execution: {execution_name}",
                        started,
                        [],
                        {"executions": execution_results},
                    )
                data_chain = result["data"]
        except Exception as e:
            logging.exception("Pipeline failed: %s", pipeline_name)
            return self._result(False, data_chain, f"Pipeline failed: {pipeline_name}, error: {e}", started)

        logging.info('<<<<<<<<<<<<<<<<<<<<<-  Successfully RUN Pipeline: %s - >>>>>>>>>>>>>>>>>>>>>', pipeline_name)
        return self._result(True, data_chain, None, started, [], {"executions": execution_results})

    def get_tools(self) -> dict:
        now = time.time()
        if self._tools_cache is not None and (now - self._tools_cache_ts) < self._TOOLS_CACHE_TTL:
            return self._tools_cache
        tools = {}
        for execution_name in Execution.get_available_executions():
            execution = Execution.get_execution(execution_name)
            if (
                    hasattr(execution, "astool")
                    and execution.astool
                    and hasattr(execution, "mcp_desc")
                    and execution.mcp_desc
            ):
                tools[execution_name] = execution.mcp_desc
        self._tools_cache = tools
        self._tools_cache_ts = now
        return tools

    def invalidate_tools_cache(self):
        self._tools_cache = None

    @staticmethod
    def _result(
            ok: bool,
            data: dict,
            error: Optional[str],
            started: float,
            skipped_tasks: Optional[list] = None,
            extra_meta: Optional[dict] = None,
    ) -> dict:
        safe_data = BackgroundRuntime._public_data(data)
        meta = {
            "duration_ms": int((time.time() - started) * 1000),
            "skipped_tasks": skipped_tasks or [],
            "aborted_tasks": [],
        }
        if extra_meta:
            meta.update(extra_meta)
        return {"ok": ok, "data": safe_data, "error": error, "meta": meta}

    @staticmethod
    def _public_data(data_chain: Any) -> dict:
        if not isinstance(data_chain, dict):
            return {}

        resp_key = HTTP_RESPONSE_KEY
        if resp_key in data_chain:
            return data_chain[data_chain[resp_key]]

        result = {}
        for key, value in data_chain.items():
            if key.startswith('__'):
                continue
            if BackgroundRuntime._is_chrome_driver_instance(value):
                continue
            try:
                json.dumps(value)
                result[key] = value
            except (TypeError, ValueError, OverflowError):
                continue
        return result

    @staticmethod
    def _is_chrome_driver_instance(value: Any) -> bool:
        cls = getattr(value, "__class__", None)
        if cls is None:
            return False

        module_name = str(getattr(cls, "__module__", "")).lower()
        class_name = str(getattr(cls, "__name__", "")).lower()
        return "selenium" in module_name and "webdriver" in module_name and "chrome" in (module_name + class_name)

    @staticmethod
    def _collect_loop_cursor(current_loop: Any, state: ExecutionState) -> str:
        idx = "" if current_loop is None else str(state.loop_times_cur) if state.is_times_loop else str(
            state.current_loop_idx)
        return (current_loop.get_loop_code() + "@" + idx) if current_loop is not None else ""

    def _log_start_process(self, seq: int, proc_name: str, loop_cursor: str, task: Task) -> None:
        logging.info(
            ">-%s >- %s >---------------> Task: %s %s -- begin >",
            task.start, proc_name, seq, loop_cursor,
        )
        logging.info("process start: %s", task.input)

    def _log_skipped_process(self, task: Task) -> None:
        logging.info("*** skipped *** : %s", task.input)

    def _log_end_process(self, seq: int, proc_name: str, loop_cursor: str, task: Task) -> None:
        logging.info(
            "<-%s <- %s <--------------< Task: %s %s -- end << \n",
            task.end, proc_name, seq, loop_cursor,
        )

    def _skip_reason(self, task: Task) -> Optional[str]:
        if getattr(task, "skipped", False):
            return "task.skipped"

        decision = decide(task.type, self.ui_policy)
        if decision == "skip":
            return "nogui-policy.skip"
        if decision == "abort":
            raise RuntimeError(
                f"No-GUI policy abort for GUI processor type={task.type}, set nogui_ui_processor_policy=skip to continue"
            )
        return None

    def on_run_execution(self, init_param: Optional[dict] = None):
        execution_name = None
        if init_param and isinstance(init_param, dict):
            execution_name = init_param.get("execution")
        if not isinstance(execution_name, str) or not execution_name:
            raise ValueError("execution name is required in init_param['execution']")
        return self.run_execution(execution_name, init_param)

    def warm_processor_cache(self) -> None:
        types_seen: set[str] = set()
        for name in Execution.get_available_executions():
            execution = Execution.get_execution(name)
            if not execution or not getattr(execution, 'astool', False):
                continue
            for task in execution.list:
                if task.type not in types_seen:
                    types_seen.add(task.type)
                    try:
                        Processor.get_processor_by_type(task.type)
                    except Exception:
                        pass
        logging.info('Processor cache warmed: %d types pre-loaded', len(types_seen))
