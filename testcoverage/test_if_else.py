"""Unit tests for IF_ELSE processor and __skip_range execution logic."""

import json
import os
import sys

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.processor import Processor
from core.task import Task


class TestIfElseProcessor:

    def _make_if_else(self, condition_fn, then_tasks=1, else_tasks=0, chain=None, run_sequence=1):
        if chain is None:
            chain = {}
        input_json = json.dumps({
            "condition_fn": condition_fn,
            "then_tasks": str(then_tasks),
            "else_tasks": str(else_tasks),
        })
        proc = Processor.get_processor_by_type("IF_ELSE")
        task = Task(type="IF_ELSE", input=input_json)
        task.data_chain = chain
        task.run_sequence = run_sequence
        proc.set_task(task)
        proc.set_view(None)
        proc.set_condition(None)
        proc.set_in_loop(False)
        return proc, chain

    def test_condition_true_no_else(self):
        proc, chain = self._make_if_else("return True", then_tasks=2, else_tasks=0)
        proc.process()
        assert '__skip_range' not in chain

    def test_condition_true_with_else(self):
        proc, chain = self._make_if_else("return True", then_tasks=2, else_tasks=3, run_sequence=1)
        proc.process()
        assert chain['__skip_range'] == (4, 6)

    def test_condition_false_skip_then(self):
        proc, chain = self._make_if_else("return False", then_tasks=2, else_tasks=1, run_sequence=1)
        proc.process()
        assert chain['__skip_range'] == (2, 3)

    def test_condition_false_no_then(self):
        proc, chain = self._make_if_else("return False", then_tasks=0, else_tasks=2)
        proc.process()
        assert '__skip_range' not in chain

    def test_condition_uses_data_chain(self):
        chain = {"status": "fail"}
        proc, chain = self._make_if_else(
            "return data_chain.get('status') == 'ok'",
            then_tasks=1, else_tasks=1, chain=chain, run_sequence=5)
        proc.process()
        # FALSE → skip then (task 6)
        assert chain['__skip_range'] == (6, 6)

    def test_condition_true_uses_data_chain(self):
        chain = {"status": "ok"}
        proc, chain = self._make_if_else(
            "return data_chain.get('status') == 'ok'",
            then_tasks=1, else_tasks=1, chain=chain, run_sequence=5)
        proc.process()
        # TRUE → skip else (task 7)
        assert chain['__skip_range'] == (7, 7)


class TestSkipRangeInExecution:

    def test_skip_range_integration(self):
        """Test that __skip_range causes tasks to be skipped during execution."""
        from core.execution import Execution
        from threading import Condition

        tasks = [
            Task(type="IF_ELSE", input='{"condition_fn":"return False", "then_tasks":"1", "else_tasks":"0"}'),
            Task(type="WAIT_SECONDS", input='{"wait_seconds":"0"}'),
            Task(type="ENCODE_DECODE_STR", input='{"type":"encode", "inbound":"test", "algorithms":"base64", "outbound_key":"result"}'),
        ]
        execution = Execution(
            execution="test_if_else",
            list=tasks,
            mcp_desc='',
            astool=False,
            loops=[]
        )
        cond = Condition()
        result = execution.run({}, cond, None)
        # IF_ELSE condition is False, then_tasks=1 → task 2 (WAIT_SECONDS) should be skipped
        # task 3 (ENCODE_DECODE_STR) should run
        assert "result" in result
        assert result["result"] == "dGVzdA=="

    def test_skip_range_condition_true(self):
        """When condition is True and else_tasks=1, the else task is skipped."""
        from core.execution import Execution
        from threading import Condition

        tasks = [
            Task(type="IF_ELSE", input='{"condition_fn":"return True", "then_tasks":"1", "else_tasks":"1"}'),
            Task(type="ENCODE_DECODE_STR", input='{"type":"encode", "inbound":"then_ran", "algorithms":"base64", "outbound_key":"then_result"}'),
            Task(type="ENCODE_DECODE_STR", input='{"type":"encode", "inbound":"else_ran", "algorithms":"base64", "outbound_key":"else_result"}'),
        ]
        execution = Execution(
            execution="test_if_else_true",
            list=tasks,
            mcp_desc='',
            astool=False,
            loops=[]
        )
        cond = Condition()
        result = execution.run({}, cond, None)
        # then-block (task 2) should run, else-block (task 3) should be skipped
        assert "then_result" in result
        assert "else_result" not in result
