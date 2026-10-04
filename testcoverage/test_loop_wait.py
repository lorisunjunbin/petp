"""Tests for loop inter-iteration wait (wait_seconds)."""

import json
import time
from threading import Condition

import pytest

from core.loop import Loop
from core.execution import Execution
from core.task import Task


def _build_execution(loop_attrs, body_tasks):
    """In-memory Execution: body tasks form the loop body (task_start=1).
    Collections, if any, are passed via ex.run(init_data, ...). No disk YAML."""
    loop = Loop("wloop", json.dumps(loop_attrs))
    ex = Execution(execution="__mem_wait_test", list=list(body_tasks),
                   mcp_desc="", astool=False, loops=[loop])
    return ex


class TestWaitSecondsSchema:

    def test_tpl_contains_wait_seconds(self):
        tpl = json.loads(Loop.tpl())
        assert "wait_seconds" in tpl
        assert tpl["wait_seconds"] == "0"

    def test_get_wait_seconds_present(self, make_loop):
        assert make_loop(wait_seconds="30").get_wait_seconds() == "30"

    def test_get_wait_seconds_missing_defaults_zero(self):
        legacy = Loop("legacy", json.dumps({"task_start": 1, "task_end": 1}))
        assert legacy.get_wait_seconds() == "0"


class TestWaitBetweenIterations:

    def _times_loop_attrs(self, wait_seconds, times="3"):
        return {
            "task_start": 1, "task_end": 1,
            "loop_key": "", "loop_times": times,
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "", "loop_condition": "", "terminate_msg": "",
            "wait_seconds": wait_seconds,
        }

    def test_wait_adds_delay_between_iterations(self):
        # 3 iterations, 0.3s wait → 2 gaps → >= 0.6s total.
        attrs = self._times_loop_attrs("0.3", times="3")
        body = [Task(type="INITIAL_PARAMS", input='{"noop":"1"}')]
        ex = _build_execution(attrs, body)
        start = time.monotonic()
        ex.run({}, Condition(), None)
        elapsed = time.monotonic() - start
        assert elapsed >= 0.55, f"expected >= ~0.6s (2 gaps x 0.3s), got {elapsed:.2f}s"

    def test_no_wait_when_zero(self):
        attrs = self._times_loop_attrs("0", times="3")
        body = [Task(type="INITIAL_PARAMS", input='{"noop":"1"}')]
        ex = _build_execution(attrs, body)
        start = time.monotonic()
        ex.run({}, Condition(), None)
        elapsed = time.monotonic() - start
        assert elapsed < 0.3, f"expected fast (no wait), got {elapsed:.2f}s"

    def test_wait_seconds_expression(self):
        # wait_seconds references a data_chain var resolved via expression2str.
        attrs = self._times_loop_attrs("{delay}", times="2")
        body = [Task(type="INITIAL_PARAMS", input='{"noop":"1"}')]
        ex = _build_execution(attrs, body)
        start = time.monotonic()
        ex.run({"delay": "0.3"}, Condition(), None)
        elapsed = time.monotonic() - start
        assert elapsed >= 0.25, f"expected >= ~0.3s (1 gap), got {elapsed:.2f}s"

    def test_last_iteration_no_trailing_wait(self):
        # 2 iterations with 0.3s wait → exactly 1 gap (~0.3s), not 2 (~0.6s).
        attrs = self._times_loop_attrs("0.3", times="2")
        body = [Task(type="INITIAL_PARAMS", input='{"noop":"1"}')]
        ex = _build_execution(attrs, body)
        start = time.monotonic()
        ex.run({}, Condition(), None)
        elapsed = time.monotonic() - start
        assert 0.25 <= elapsed < 0.55, f"expected ~0.3s (1 gap only), got {elapsed:.2f}s"
