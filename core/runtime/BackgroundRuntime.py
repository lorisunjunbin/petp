import json
import logging
import time
from threading import Condition
from typing import Any, Optional

from core.execution import Execution
from core.executionstate import ExecutionState
from core.pipeline import Pipeline
from core.processor import Processor
from core.runtime.UiProcessorPolicy import decide
from core.task import Task
from httpservice.handlers.HttpRequestHandler import HttpRequestHandler
from utils.DateUtil import DateUtil


class BackgroundRuntime:
    def __init__(self, model: Any, ui_policy: str = "skip"):
        self.model = model
        self.ui_policy = ui_policy

    def run_execution(self, execution_name: str, init_data: Optional[dict] = None) -> dict:
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

                self._log_start_process(current_loop, state, processor, task)

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
                            self._log_end_process(current_loop, state, processor, task)
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
                self._log_end_process(current_loop, state, processor, task)

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
                    state.current_index = int(goto_target) - 1
                    logging.info('GO_TO_TASK: jumping to task %s', goto_target)
                    continue

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

        data_chain = dict(init_data or {})
        execution_results = []

        try:
            for execution_def in pipeline.list:
                execution_name = execution_def.get("execution")
                execution_input = pipeline.load_proper_input(execution_def)
                merged_input = dict(data_chain)
                merged_input.update(execution_input)

                result = self.run_execution(execution_name, merged_input)
                execution_results.append({"execution": execution_name, "result": result})

                if not result["ok"]:
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

        return self._result(True, data_chain, None, started, [], {"executions": execution_results})

    def get_tools(self) -> dict:
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
        return tools

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

        resp_key = HttpRequestHandler.get_response_key()
        if resp_key in data_chain:
            return data_chain[data_chain[resp_key]]

        result = {}
        for key, value in data_chain.items():
            if key in {"__m", "__p"} or BackgroundRuntime._should_skip_public_value(value):
                continue
            result[key] = value

        return result

    @staticmethod
    def _should_skip_public_value(value: Any) -> bool:
        return BackgroundRuntime._is_chrome_driver_instance(value) or not BackgroundRuntime._is_json_serializable(value)

    @staticmethod
    def _is_chrome_driver_instance(value: Any) -> bool:
        cls = getattr(value, "__class__", None)
        if cls is None:
            return False

        module_name = str(getattr(cls, "__module__", "")).lower()
        class_name = str(getattr(cls, "__name__", "")).lower()
        return "selenium" in module_name and "webdriver" in module_name and "chrome" in (module_name + class_name)

    @staticmethod
    def _is_json_serializable(value: Any) -> bool:
        try:
            json.dumps(value)
            return True
        except (TypeError, OverflowError):
            return False

    @staticmethod
    def _collect_loop_cursor(current_loop: Any, state: ExecutionState) -> str:
        idx = "" if current_loop is None else str(state.loop_times_cur) if state.is_times_loop else str(
            state.current_loop_idx)
        return (current_loop.get_loop_code() + "@" + idx) if current_loop is not None else ""

    def _log_start_process(self, current_loop: Any, state: ExecutionState, processor: Processor, task: Task) -> None:
        loop_cursor = self._collect_loop_cursor(current_loop, state)
        logging.info(
            f">-{task.start} >- {type(processor).__name__} >---------------> Task: {state.get_sequence()} {loop_cursor} -- begin >"
        )
        logging.info(f"process start: {task.input}")

    def _log_skipped_process(self, task: Task) -> None:
        logging.info(f"*** skipped *** : {task.input}")

    def _log_end_process(self, current_loop: Any, state: ExecutionState, processor: Processor, task: Task) -> None:
        loop_cursor = self._collect_loop_cursor(current_loop, state)
        logging.info(
            f"<-{task.end} <- {type(processor).__name__} <--------------< Task: {state.get_sequence()} {loop_cursor} -- end << \n"
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
