"""Tests for loop terminate behavior (exception_then=terminate / loop_condition terminate)."""

import json
from threading import Condition

import pytest

from core.execution import Execution
from core.loop import Loop, LoopTerminateError
from core.task import Task


def _build_execution(loop_attrs, body_tasks):
    """内存构造一个 Execution:循环体 tasks 从 task 1 开始 (loop 覆盖 task 1..N)。
    items 直接由调用方通过 ex.run(initial_data, ...) 传入,不写磁盘 YAML。"""
    loop = Loop("tloop", json.dumps(loop_attrs))
    ex = Execution(execution="__mem_terminate_test", list=body_tasks, mcp_desc="", astool=False, loops=[loop])
    return ex


class TestLoopTerminateSchema:

    def test_terminate_error_is_exception(self):
        assert issubclass(LoopTerminateError, Exception)

    def test_tpl_contains_terminate_msg(self):
        tpl = json.loads(Loop.tpl())
        assert "terminate_msg" in tpl
        assert tpl["terminate_msg"] == ""

    def test_get_terminate_msg_present(self, make_loop):
        loop = make_loop(terminate_msg="boom {loop_item}")
        assert loop.get_terminate_msg() == "boom {loop_item}"

    def test_get_terminate_msg_missing_defaults_empty(self):
        # 旧 loop:JSON 里没有 terminate_msg key
        loop = Loop("legacy", json.dumps({"task_start": 2, "task_end": 5}))
        assert loop.get_terminate_msg() == ""

    def test_get_exception_then_terminate(self, make_loop):
        assert make_loop(exception_then="terminate").get_exception_then() == "terminate"


class TestExecutionTerminateOnException:

    def test_task_exception_terminate_raises(self):
        # loop 覆盖 task 1(READ_JSON 读不存在文件 → 抛异常)
        loop_attrs = {
            "task_start": 1, "task_end": 1,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "terminate",
            "loop_condition": "",
            "terminate_msg": "stopped at {loop_item}",
        }
        body = [Task(type="READ_JSON", input='{"file_path":"/no/such/file_xyz.json","data_key":"j"}')]
        ex = _build_execution(loop_attrs, body)
        with pytest.raises(LoopTerminateError) as ei:
            ex.run({"items": ["a", "b", "c"]}, Condition(), None)
        assert "stopped at a" in str(ei.value)  # 第一次迭代 loop_item='a'

    def test_task_exception_unknown_policy_propagates_original(self):
        # exception_then 拼错 → 不进入 terminate 分支,原始异常照常抛出(非 LoopTerminateError)
        loop_attrs = {
            "task_start": 1, "task_end": 1,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "terminat",  # typo
            "loop_condition": "", "terminate_msg": "",
        }
        body = [Task(type="READ_JSON", input='{"file_path":"/no/such/file_xyz.json","data_key":"j"}')]
        ex = _build_execution(loop_attrs, body)
        with pytest.raises(Exception) as ei:
            ex.run({"items": ["a", "b", "c"]}, Condition(), None)
        assert not isinstance(ei.value, LoopTerminateError)

    def test_task_exception_terminate_empty_msg_uses_default(self):
        loop_attrs = {
            "task_start": 1, "task_end": 1,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "terminate",
            "loop_condition": "", "terminate_msg": "",
        }
        body = [Task(type="READ_JSON", input='{"file_path":"/no/such/file_xyz.json","data_key":"j"}')]
        ex = _build_execution(loop_attrs, body)
        with pytest.raises(LoopTerminateError) as ei:
            ex.run({"items": ["a", "b", "c"]}, Condition(), None)
        msg = str(ei.value)
        assert "tloop" in msg          # 默认消息含 loop_code
        assert "task 1" in msg         # 含 task 序号


class TestExecutionTerminateOnCondition:

    def test_loop_condition_terminate_raises(self):
        loop_attrs = {
            "task_start": 1, "task_end": 1,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "",
            "loop_condition": "return True, 'terminate'",
            "terminate_msg": "cond stop {loop_item}",
        }
        body = [Task(type="INITIAL_PARAMS", input='{"noop":"1"}')]
        ex = _build_execution(loop_attrs, body)
        with pytest.raises(LoopTerminateError) as ei:
            ex.run({"items": ["a", "b", "c"]}, Condition(), None)
        assert "cond stop a" in str(ei.value)

    def test_loop_condition_terminate_empty_msg_default(self):
        loop_attrs = {
            "task_start": 1, "task_end": 1,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "",
            "loop_condition": "return True, 'terminate'",
            "terminate_msg": "",
        }
        body = [Task(type="INITIAL_PARAMS", input='{"noop":"1"}')]
        ex = _build_execution(loop_attrs, body)
        with pytest.raises(LoopTerminateError) as ei:
            ex.run({"items": ["a", "b", "c"]}, Condition(), None)
        assert "tloop" in str(ei.value)
        assert "task 1" in str(ei.value)


class TestTerminateMsgExpression:

    def test_terminate_msg_unresolved_var_falls_back(self):
        loop_attrs = {
            "task_start": 1, "task_end": 1,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "",
            "loop_condition": "return True, 'terminate'",
            "terminate_msg": "ref {nonexistent_var_xyz}",
        }
        body = [Task(type="INITIAL_PARAMS", input='{"noop":"1"}')]
        ex = _build_execution(loop_attrs, body)
        with pytest.raises(LoopTerminateError) as ei:
            ex.run({"items": ["a", "b", "c"]}, Condition(), None)
        # expression2str 对未解析变量兜底返回原串;不得崩成其它异常
        assert "nonexistent_var_xyz" in str(ei.value)


class TestBackgroundRuntimeTerminate:

    def _run_mem_execution_in_bg(self, ex, init_data=None):
        """用 BackgroundRuntime 跑内存构造的 Execution(不写磁盘 YAML)。
        通过 monkeypatch Execution.get_execution 让 BG 拿到内存对象。"""
        import os
        import core.runtime.BackgroundRuntime as bg_mod
        from mvp.model.PETPModel import PETPModel
        from utils.SystemConfig import SystemConfig
        from core.execution import Execution as ExecClass

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)

        model = PETPModel(SystemConfig("petpconfig.yaml"))
        runtime = bg_mod.BackgroundRuntime(model, ui_policy="skip")

        orig = ExecClass.get_execution
        ExecClass.get_execution = staticmethod(lambda name: ex if name == ex.execution else orig(name))
        try:
            return runtime.run_execution(ex.execution, init_data or {})
        finally:
            ExecClass.get_execution = staticmethod(orig)

    def test_bg_task_exception_terminate_returns_not_ok(self):
        loop_attrs = {
            "task_start": 2, "task_end": 2,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "terminate",
            "loop_condition": "", "terminate_msg": "bg stop {loop_item}",
        }
        body = [
            Task(type="INITIAL_PARAMS", input='{"noop":"1"}'),
            Task(type="READ_JSON", input='{"file_path":"/no/such/file_xyz.json","data_key":"j"}'),
        ]
        loop = __import__("core.loop", fromlist=["Loop"]).Loop("tloop", __import__("json").dumps(loop_attrs))
        ex = Execution(execution="__mem_bg_terminate_test", list=body, mcp_desc="", astool=False, loops=[loop])
        r = self._run_mem_execution_in_bg(ex, {"items": ["a", "b", "c"]})
        assert r["ok"] is False
        assert "bg stop a" in str(r["error"])

    def test_bg_loop_condition_terminate_returns_not_ok(self):
        loop_attrs = {
            "task_start": 2, "task_end": 2,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "",
            "loop_condition": "return True, 'terminate'",
            "terminate_msg": "bg cond stop",
        }
        body = [
            Task(type="INITIAL_PARAMS", input='{"noop":"1"}'),
            Task(type="INITIAL_PARAMS", input='{"noop":"1"}'),
        ]
        loop = __import__("core.loop", fromlist=["Loop"]).Loop("tloop", __import__("json").dumps(loop_attrs))
        ex = Execution(execution="__mem_bg_cond_terminate_test", list=body, mcp_desc="", astool=False, loops=[loop])
        r = self._run_mem_execution_in_bg(ex, {"items": ["a", "b", "c"]})
        assert r["ok"] is False
        assert "bg cond stop" in str(r["error"])


class TestDualRuntimeConsistency:

    def test_main_raises_bg_returns_not_ok_same_msg(self):
        loop_attrs = {
            "task_start": 2, "task_end": 2,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "terminate",
            "loop_condition": "", "terminate_msg": "unified {loop_item}",
        }
        # Main runtime test
        body_main = [
            Task(type="INITIAL_PARAMS", input='{"noop":"1"}'),
            Task(type="READ_JSON", input='{"file_path":"/no/such/file_xyz.json","data_key":"j"}'),
        ]
        loop_main = __import__("core.loop", fromlist=["Loop"]).Loop("tloop", __import__("json").dumps(loop_attrs))
        ex_main = Execution(execution="__mem_dual_test_main", list=body_main, mcp_desc="", astool=False, loops=[loop_main])
        with pytest.raises(LoopTerminateError) as ei:
            ex_main.run({"items": ["a", "b", "c"]}, Condition(), None)
        main_msg = str(ei.value)

        # BG runtime test
        body_bg = [
            Task(type="INITIAL_PARAMS", input='{"noop":"1"}'),
            Task(type="READ_JSON", input='{"file_path":"/no/such/file_xyz.json","data_key":"j"}'),
        ]
        loop_bg = __import__("core.loop", fromlist=["Loop"]).Loop("tloop", __import__("json").dumps(loop_attrs))
        ex_bg = Execution(execution="__mem_dual_test", list=body_bg, mcp_desc="", astool=False, loops=[loop_bg])
        r = TestBackgroundRuntimeTerminate()._run_mem_execution_in_bg(ex_bg, {"items": ["a", "b", "c"]})
        assert r["ok"] is False
        assert "unified a" in main_msg
        assert "unified a" in str(r["error"])
