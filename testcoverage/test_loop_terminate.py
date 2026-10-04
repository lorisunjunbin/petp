"""Tests for loop terminate behavior (exception_then=terminate / loop_condition terminate)."""

import json

import pytest

from core.loop import Loop, LoopTerminateError


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
