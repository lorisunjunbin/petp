import json
import time
import unittest
from queue import SimpleQueue

from httpservice.BackgroundHttpServer import BackgroundHttpServer


class _FakeHandler:
    def __init__(self, accept="text/event-stream", auth="Bearer t"):
        self.headers = {"Accept": accept, "Authorization": auth}


class _FakeRuntime:
    def __init__(self, result=None, raise_exc=None, progress_msgs=None, sleep=0.0):
        self._result = result or {"ok": True, "data": {}, "error": None, "meta": {}}
        self._raise = raise_exc
        self._progress_msgs = progress_msgs or []
        self._sleep = sleep

    def run_execution(self, name, params, progress_queue=None):
        for m in self._progress_msgs:
            if progress_queue is not None:
                progress_queue.put(m)
        if self._sleep:
            time.sleep(self._sleep)
        if self._raise:
            raise self._raise
        return self._result

    def run_pipeline(self, name, params, progress_queue=None):
        if progress_queue is not None:
            progress_queue.put({"type": "execution", "pipeline": name, "exec": "step1", "phase": "started"})
            progress_queue.put({"type": "task", "execution": "step1", "index": 1, "total": 1,
                                "task_type": "ECHO", "phase": "started"})
            progress_queue.put({"type": "task", "execution": "step1", "index": 1, "total": 1,
                                "task_type": "ECHO", "phase": "done", "duration_ms": 5})
            progress_queue.put({"type": "execution", "pipeline": name, "exec": "step1", "phase": "done"})
        return self._result

    def get_tools(self):
        return {}


def _collect(stream_data):
    return list(stream_data.iterator)


def _make_server(runtime, token="t"):
    return BackgroundHttpServer(runtime, port=0, timeout=10, token=token)


class TestSseHappyPath(unittest.TestCase):
    def test_execution_emits_progress_then_result(self):
        runtime = _FakeRuntime(
            result={"ok": True, "data": {"foo": "bar"}, "error": None, "meta": {}},
            progress_msgs=[
                {"type": "task", "execution": "MY", "index": 1, "total": 2,
                 "task_type": "X", "phase": "started"},
                {"type": "task", "execution": "MY", "index": 1, "total": 2,
                 "task_type": "X", "phase": "done", "duration_ms": 3},
            ],
        )
        srv = _make_server(runtime)
        sd = srv._stream_exec_result("execution", {"execution": "MY"})
        events = _collect(sd)
        joined = "".join(events)
        assert "event: progress" in joined
        assert "event: result" in joined
        # last event is the result frame
        assert events[-1].startswith("event: result\n")

    def test_pipeline_emits_execution_and_task_events(self):
        runtime = _FakeRuntime()
        srv = _make_server(runtime)
        sd = srv._stream_exec_result("pipeline", {"pipeline": "P"})
        joined = "".join(_collect(sd))
        assert '"type": "execution"' in joined
        assert '"type": "task"' in joined


class TestSseError(unittest.TestCase):
    def test_execution_exception_yields_result_with_ok_false(self):
        runtime = _FakeRuntime(raise_exc=RuntimeError("boom"))
        srv = _make_server(runtime)
        sd = srv._stream_exec_result("execution", {"execution": "MY"})
        events = _collect(sd)
        last_data = events[-1].split("data: ", 1)[1].strip()
        payload = json.loads(last_data)
        assert payload["ok"] is False
        assert "boom" in (payload.get("error") or "")

    def test_missing_execution_param_yields_immediate_error(self):
        runtime = _FakeRuntime()
        srv = _make_server(runtime)
        sd = srv._stream_exec_result("execution", {})
        events = _collect(sd)
        assert len(events) == 1
        assert events[0].startswith("event: result\n")
        payload = json.loads(events[0].split("data: ", 1)[1].strip())
        assert payload["ok"] is False


class TestSseAuth(unittest.TestCase):
    def test_auth_failure_returns_tuple_not_stream(self):
        runtime = _FakeRuntime()
        srv = _make_server(runtime, token="real")
        handler = _FakeHandler(auth="Bearer wrong")
        result = srv._handle_petp_exec(handler, {"action": "execution", "params": {"execution": "MY"}})
        assert isinstance(result, tuple)
        assert result[1] == 401

    def test_no_token_configured_returns_501(self):
        runtime = _FakeRuntime()
        srv = _make_server(runtime, token=None)
        handler = _FakeHandler()
        result = srv._handle_petp_exec(handler, {"action": "execution", "params": {"execution": "MY"}})
        assert isinstance(result, tuple)
        assert result[1] == 501


class TestSseHeartbeat(unittest.TestCase):
    def test_heartbeat_emitted_when_runtime_idle(self):
        # 1.5s sleep > 1s heartbeat interval => at least one heartbeat
        runtime = _FakeRuntime(sleep=1.5)
        srv = _make_server(runtime)
        sd = srv._stream_exec_result("execution", {"execution": "MY"})
        joined = "".join(_collect(sd))
        assert '"type": "heartbeat"' in joined


if __name__ == "__main__":
    unittest.main()
