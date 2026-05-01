"""Shared pytest fixtures for PETP test suite."""

import json
import os
import sys

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.processor import Processor
from core.task import Task
from core.loop import Loop
from core.executionstate import ExecutionState


@pytest.fixture
def data_chain():
    """Fresh data_chain dict for each test."""
    return {}


@pytest.fixture
def make_processor():
    """Factory fixture: creates a Processor instance with a fake Task."""

    def _factory(processor_type, input_json=None, chain=None):
        if input_json is None:
            input_json = '{}'
        if chain is None:
            chain = {}

        proc = Processor.get_processor_by_type(processor_type)
        task = Task(type=processor_type, input=input_json)
        task.data_chain = chain
        proc.set_task(task)
        proc.set_view(None)
        proc.set_condition(None)
        proc.set_in_loop(False)
        return proc

    return _factory


@pytest.fixture
def make_loop():
    """Factory fixture: creates a Loop instance from attributes dict."""

    def _factory(code="test_loop", **attrs):
        defaults = {
            "task_start": 2,
            "task_end": 5,
            "loop_key": "",
            "loop_times": "0",
            "loop_index_key": "loop_idx",
            "item_key": "loop_item",
            "exception_then": "",
            "loop_condition": "",
        }
        defaults.update(attrs)
        return Loop(code, json.dumps(defaults))

    return _factory


@pytest.fixture(scope="session")
def bg_runtime():
    """Session-scoped BackgroundRuntime for integration tests."""
    from core.runtime.BackgroundRuntime import BackgroundRuntime
    from mvp.model.PETPModel import PETPModel
    from utils.SystemConfig import SystemConfig

    os.chdir(PROJECT_ROOT)
    model = PETPModel(SystemConfig("petpconfig.yaml"))
    return BackgroundRuntime(model, ui_policy="skip")
