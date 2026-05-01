"""Unit tests for ExecutionState loop methods and Loop validation."""

import json

import pytest

from core.loop import Loop
from core.executionstate import ExecutionState


class TestLoopVerification:

    def test_valid_times_loop(self, make_loop):
        loop = make_loop(loop_times="3", loop_key="")
        loop.verify_loop()

    def test_valid_collection_loop(self, make_loop):
        loop = make_loop(loop_times="0", loop_key="my_list")
        loop.verify_loop()

    def test_both_set_raises_value_error(self, make_loop):
        loop = make_loop(loop_times="3", loop_key="my_list")
        with pytest.raises(ValueError, match="loop_times and loop_key can not be used together"):
            loop.verify_loop()

    def test_is_loop_for_times(self, make_loop):
        assert make_loop(loop_times="5", loop_key="").is_loop_for_times() is True
        assert make_loop(loop_times="0", loop_key="items").is_loop_for_times() is False

    def test_get_exception_then(self, make_loop):
        assert make_loop(exception_then="break").get_exception_then() == "break"
        assert make_loop(exception_then="continue").get_exception_then() == "continue"
        assert make_loop(exception_then="").get_exception_then() == ""

    def test_get_loop_condition(self, make_loop):
        assert make_loop(loop_condition="return True,'break'").get_loop_condition() == "return True,'break'"
        assert make_loop(loop_condition="").get_loop_condition() == ""


class TestExecutionStateTimesLoop:

    def _make_state_with_loop(self, make_loop, task_count=6, loop_times=3):
        tasks = [None] * task_count
        state = ExecutionState(tasks)
        loop = make_loop(task_start=2, task_end=5, loop_times=str(loop_times), loop_key="")
        state.current_index = 1  # at task_start (0-based = task_start - 1)
        state.init_loop(loop)
        return state, loop

    def test_init_loop_flags(self, make_loop):
        tasks = [None] * 6
        state = ExecutionState(tasks)
        loop = make_loop(task_start=2, task_end=5, loop_times="3", loop_key="")

        state.current_index = 1  # sequence = 2 = task_start
        state.init_loop(loop)
        assert state.is_loop_execution is True
        assert state.is_times_loop is True
        assert state.is_loop_start is True
        assert state.is_loop_end is False

    def test_setup_loop_start_times(self, make_loop):
        state, loop = self._make_state_with_loop(make_loop, loop_times=3)
        data_chain = {}
        state.setup_loop_start(data_chain)
        assert state.loop_times == 3
        assert data_chain["loop_idx"] == 0

    def test_loop_end_continue_advances(self, make_loop):
        state, loop = self._make_state_with_loop(make_loop, loop_times=3)
        data_chain = {"loop_idx": 0}
        state.setup_loop_start(data_chain)

        state.current_index = 4  # at task_end (0-based)
        result = state.setup_loop_end_then_continue(data_chain)
        assert result is True
        assert state.loop_times_cur == 1
        assert data_chain["loop_idx"] == 1
        assert state.current_index == 1  # back to task_start - 1

    def test_loop_end_exhausted(self, make_loop):
        state, loop = self._make_state_with_loop(make_loop, loop_times=2)
        data_chain = {"loop_idx": 0}
        state.setup_loop_start(data_chain)

        # First iteration end
        state.current_index = 4
        state.setup_loop_end_then_continue(data_chain)
        # Second iteration end (last)
        state.current_index = 4
        result = state.setup_loop_end_then_continue(data_chain)
        assert result is None
        assert state.loop_times_cur == 0
        assert state.loop_times == 0


class TestExecutionStateCollectionLoop:

    def test_setup_loop_start_collection(self, make_loop):
        tasks = [None] * 6
        state = ExecutionState(tasks)
        loop = make_loop(task_start=2, task_end=5, loop_times="0", loop_key="items")
        state.current_index = 1
        state.init_loop(loop)

        data_chain = {"items": ["a", "b", "c"], "loop_idx": 0}
        state.setup_loop_start(data_chain)

        assert data_chain["loop_item"] == "a"
        assert data_chain["loop_idx"] == 0
        assert state.current_loop_collection == ["a", "b", "c"]

    def test_setup_loop_start_json_string_collection(self, make_loop):
        tasks = [None] * 6
        state = ExecutionState(tasks)
        loop = make_loop(task_start=2, task_end=5, loop_times="0", loop_key="items")
        state.current_index = 1
        state.init_loop(loop)

        data_chain = {"items": '["x", "y"]', "loop_idx": 0}
        state.setup_loop_start(data_chain)

        assert data_chain["items"] == ["x", "y"]
        assert data_chain["loop_item"] == "x"

    def test_collection_loop_advances(self, make_loop):
        tasks = [None] * 6
        state = ExecutionState(tasks)
        loop = make_loop(task_start=2, task_end=5, loop_times="0", loop_key="items")
        state.current_index = 1
        state.init_loop(loop)

        data_chain = {"items": ["a", "b", "c"], "loop_idx": 0}
        state.setup_loop_start(data_chain)

        state.current_index = 4
        result = state.setup_loop_end_then_continue(data_chain)
        assert result is True
        assert state.current_loop_idx == 1
        assert data_chain["loop_idx"] == 1

    def test_collection_loop_exhausted(self, make_loop):
        tasks = [None] * 6
        state = ExecutionState(tasks)
        loop = make_loop(task_start=2, task_end=5, loop_times="0", loop_key="items")
        state.current_index = 1
        state.init_loop(loop)

        data_chain = {"items": ["a"], "loop_idx": 0}
        state.setup_loop_start(data_chain)

        state.current_index = 4
        result = state.setup_loop_end_then_continue(data_chain)
        assert result is None
        assert data_chain["loop_item"] is None


class TestExceptionHandling:

    def test_advance_loop_on_exception_more_iterations(self, make_loop):
        tasks = [None] * 6
        state = ExecutionState(tasks)
        loop = make_loop(task_start=2, task_end=5, loop_times="3", loop_key="")
        state.current_index = 2  # somewhere in the loop
        state.init_loop(loop)

        data_chain = {"loop_idx": 0}
        state.setup_loop_start(data_chain)

        result = state.advance_loop_on_exception(data_chain)
        assert result is True
        assert state.current_index == 1  # back to task_start - 1

    def test_advance_loop_on_exception_last_iteration(self, make_loop):
        tasks = [None] * 6
        state = ExecutionState(tasks)
        loop = make_loop(task_start=2, task_end=5, loop_times="1", loop_key="")
        state.current_index = 2
        state.init_loop(loop)

        data_chain = {"loop_idx": 0}
        state.setup_loop_start(data_chain)

        result = state.advance_loop_on_exception(data_chain)
        assert result is False

    def test_force_exit_loop(self, make_loop):
        tasks = [None] * 6
        state = ExecutionState(tasks)
        loop = make_loop(task_start=2, task_end=5, loop_times="3", loop_key="")
        state.current_index = 2
        state.init_loop(loop)

        data_chain = {"loop_idx": 0}
        state.setup_loop_start(data_chain)

        state.force_exit_loop(data_chain)
        assert state.loop_times == 0
        assert state.loop_times_cur == 0
        assert data_chain["loop_idx"] == 0
        assert state.current_index == 4  # task_end - 1


class TestStateNavigation:

    def test_has_next(self):
        state = ExecutionState([None, None, None])
        assert state.has_next() is True
        state.current_index = 2
        assert state.has_next() is True
        state.current_index = 3
        assert state.has_next() is False

    def test_move_to_next(self):
        state = ExecutionState([None, None])
        assert state.current_index == 0
        state.move_to_next()
        assert state.current_index == 1

    def test_get_sequence_is_1_based(self):
        state = ExecutionState([None, None])
        state.current_index = 0
        assert state.get_sequence() == 1
        state.current_index = 1
        assert state.get_sequence() == 2
