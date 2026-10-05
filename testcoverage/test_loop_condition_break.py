"""End-to-end tests: loop_condition can break a time-based loop by reading a
value that an in-loop collect/convert processor wrote. Reproduces the bug where
FIND_THEN_COLLECT stored supplier_found only under data_chain[loop_code][idx],
so loop_condition reading the top-level key never saw it and never broke."""

import json
from threading import Condition

from core.execution import Execution
from core.loop import Loop
from core.task import Task


def _run_times_loop(loop_times, loop_condition):
    """Build a 1-task time-based loop whose body (DATA_CONVERT) writes the
    current iteration index to a top-level key 'probe', then runs loop_condition.
    Returns the final data_chain."""
    loop_attrs = {
        "task_start": 1, "task_end": 1,
        "loop_key": "", "loop_times": str(loop_times),
        "loop_index_key": "loop_idx", "item_key": "",
        "exception_then": "break",
        "loop_condition": loop_condition,
        "terminate_msg": "", "wait_seconds": "0",
    }
    loop = Loop("probe_loop", json.dumps(loop_attrs))
    body = [Task(
        type="DATA_CONVERT",
        input='{"given_key":"loop_idx","convertor_func":"return given","target_key":"probe"}',
    )]
    ex = Execution(execution="__mem_cond_break", list=body, mcp_desc="", astool=False, loops=[loop])
    return ex.run({}, Condition(), None)


class TestLoopConditionBreak:

    def test_break_when_top_level_value_matches(self):
        # loop_times=5 but loop_condition breaks once probe (== loop_idx) reaches 2.
        cond = (
            "if data_chain.get('probe') is not None and data_chain['probe'] >= 2:\\n"
            "    return True, 'break'\\n"
            "return False, ''"
        )
        chain = _run_times_loop(5, cond)
        # broke at iteration idx==2, so the last mirrored value is 2 (not 4).
        assert chain["probe"] == 2

    def test_runs_all_iterations_when_condition_never_true(self):
        cond = "return False, ''"
        chain = _run_times_loop(3, cond)
        # ran idx 0,1,2 fully; last mirrored value is 2.
        assert chain["probe"] == 2

    def test_break_on_first_iteration(self):
        cond = (
            "if data_chain.get('probe') is not None:\\n"
            "    return True, 'break'\\n"
            "return False, ''"
        )
        chain = _run_times_loop(10, cond)
        # probe set on iteration 0 → breaks immediately after first iteration.
        assert chain["probe"] == 0
