"""Unit tests for Cron circuit breaker + on_record callback wiring.

Avoids the scheduling loop by exercising _post_run_update directly,
plus a small integration check on add_one/stop_one resetting state.
"""

import pytest

from core.cron.cron import Cron


class _FakeRunnable:
    """Minimal RunnableAsCron stand-in."""

    def __init__(self, name, cron_exp="0 9 * * *"):
        self._name = name
        self._cron = cron_exp
        self.cronDesc = ""

    def get_name(self):
        return self._name

    def get_cron(self):
        return self._cron

    def get_key(self):
        return f"{self._name}_{self._cron}"

    def run_sync(self, init_data, view, cond):
        pass


@pytest.fixture
def records():
    return []


@pytest.fixture
def cron(records):
    captured = records

    def _on_record(name, exp, result):
        captured.append({"name": name, "exp": exp, "result": result})

    c = Cron(view=None, on_record=_on_record, max_consecutive_failures=3)
    yield c
    c.stop_all()


def _ok_result():
    return {"ok": True, "error": None, "data": {}, "meta": {"duration_ms": 10, "executions": []}}


def _err_result(msg="boom"):
    return {"ok": False, "error": msg, "data": {}, "meta": {"duration_ms": 10, "executions": []}}


class TestRecording:

    def test_success_records_and_clears_failures(self, cron, records):
        runnable = _FakeRunnable("PIPE_A")
        # simulate: prior failure exists, then a success arrives
        cron._consecutive_failures["PIPE_A"] = 2
        cron._post_run_update("PIPE_A", "0 9 * * *", started=0.0,
                               ok=True, error_msg=None, run_result=_ok_result(),
                               cron_obj=runnable)
        assert len(records) == 1
        assert records[0]["name"] == "PIPE_A"
        assert records[0]["result"]["ok"] is True
        # success resets the failure counter
        assert cron._consecutive_failures.get("PIPE_A", 0) == 0
        assert cron._last_status["PIPE_A"] == "ok"

    def test_failure_increments_counter_and_records(self, cron, records):
        runnable = _FakeRunnable("PIPE_B")
        cron._post_run_update("PIPE_B", "* * * * *", started=0.0,
                               ok=False, error_msg="db down", run_result=_err_result("db down"),
                               cron_obj=runnable)
        assert len(records) == 1
        assert records[0]["result"]["ok"] is False
        assert records[0]["result"]["error"] == "db down"
        assert cron._consecutive_failures["PIPE_B"] == 1
        assert cron._last_status["PIPE_B"] == "error"
        assert "db down" in cron._last_error["PIPE_B"]

    def test_synthesizes_result_when_run_returned_none(self, cron, records):
        """Old-style on_run that returns None — Cron must still produce a record."""
        runnable = _FakeRunnable("PIPE_C")
        cron._post_run_update("PIPE_C", "* * * * *", started=0.0,
                               ok=False, error_msg="kaboom", run_result=None,
                               cron_obj=runnable)
        assert len(records) == 1
        rec = records[0]["result"]
        assert rec["ok"] is False
        assert rec["error"] == "kaboom"
        assert "duration_ms" in rec["meta"]


class TestCircuitBreaker:

    def test_opens_after_threshold(self, cron):
        runnable = _FakeRunnable("PIPE_D")
        for _ in range(3):
            cron._post_run_update("PIPE_D", "* * * * *", started=0.0,
                                   ok=False, error_msg="x", run_result=_err_result(),
                                   cron_obj=runnable)
        assert "PIPE_D" in cron._suspended_until_restart
        assert cron._consecutive_failures["PIPE_D"] == 3

    def test_does_not_open_below_threshold(self, cron):
        runnable = _FakeRunnable("PIPE_E")
        for _ in range(2):
            cron._post_run_update("PIPE_E", "* * * * *", started=0.0,
                                   ok=False, error_msg="x", run_result=_err_result(),
                                   cron_obj=runnable)
        assert "PIPE_E" not in cron._suspended_until_restart

    def test_disabled_when_threshold_zero(self):
        recs = []
        c = Cron(view=None, on_record=lambda n, e, r: recs.append(r),
                  max_consecutive_failures=0)
        try:
            for _ in range(10):
                c._post_run_update("PIPE_F", "* * * * *", started=0.0,
                                    ok=False, error_msg="x", run_result=_err_result(),
                                    cron_obj=_FakeRunnable("PIPE_F"))
            assert "PIPE_F" not in c._suspended_until_restart
            assert c._consecutive_failures["PIPE_F"] == 10
        finally:
            c.stop_all()

    def test_add_one_resets_suspended_state(self, cron):
        runnable = _FakeRunnable("PIPE_G")
        # force into suspended state
        cron._suspended_until_restart.add("PIPE_G")
        cron._consecutive_failures["PIPE_G"] = 5
        cron.add_one(runnable)
        assert "PIPE_G" not in cron._suspended_until_restart
        assert "PIPE_G" not in cron._consecutive_failures
        # cleanup so stop_all doesn't try to join a runaway
        cron.stop_one(runnable)

    def test_get_running_info_exposes_breaker_fields(self, cron):
        runnable = _FakeRunnable("PIPE_H")
        cron.add_one(runnable)
        # let the worker promote it to running
        import time as _t
        for _ in range(20):
            with cron._lock:
                if runnable.get_key() in cron._running_keys:
                    break
            _t.sleep(0.05)
        # simulate a failure being recorded
        cron._consecutive_failures["PIPE_H"] = 2
        cron._last_status["PIPE_H"] = "error"
        cron._last_error["PIPE_H"] = "timeout"

        info = cron.get_running_info()
        assert any(i.get("pipeline_name") == runnable.get_key() for i in info)
        target = next(i for i in info if i.get("pipeline_name") == runnable.get_key())
        assert target["consecutive_failures"] == 2
        assert target["last_status"] == "error"
        assert target["last_error"] == "timeout"
        cron.stop_one(runnable)

    def test_record_callback_failure_does_not_crash(self):
        def boom(*a, **kw):
            raise RuntimeError("recorder offline")

        c = Cron(view=None, on_record=boom, max_consecutive_failures=3)
        try:
            # should not raise
            c._post_run_update("PIPE_I", "* * * * *", started=0.0,
                                ok=False, error_msg="x", run_result=_err_result(),
                                cron_obj=_FakeRunnable("PIPE_I"))
            # state still updated
            assert c._consecutive_failures["PIPE_I"] == 1
        finally:
            c.stop_all()
