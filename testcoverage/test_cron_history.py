"""Unit tests for CronHistory."""

import json
import os
import tempfile

import pytest

from core.cron.cron_history import CronHistory


@pytest.fixture
def history_dir(tmp_path):
    return str(tmp_path / "cron_history")


@pytest.fixture
def history(history_dir):
    return CronHistory(history_dir=history_dir, max_records=5)


def _make_result(ok=True, duration_ms=1000, error=None, executions=None):
    return {
        "ok": ok,
        "error": error,
        "data": {},
        "meta": {
            "duration_ms": duration_ms,
            "executions": executions or [
                {"execution": "step1", "result": {"ok": True, "meta": {"duration_ms": 500}}},
                {"execution": "step2", "result": {"ok": True, "meta": {"duration_ms": 500}}},
            ],
        },
    }


class TestRecord:

    def test_creates_json_file(self, history, history_dir):
        history.record("MY_PIPELINE", "0 9 * * *", _make_result())
        files = os.listdir(history_dir)
        assert len(files) == 1
        assert files[0].startswith("MY_PIPELINE_")
        assert files[0].endswith(".json")

    def test_record_content(self, history, history_dir):
        history.record("TEST_PIPE", "*/5 * * * *", _make_result(duration_ms=2000))
        files = os.listdir(history_dir)
        with open(os.path.join(history_dir, files[0])) as f:
            record = json.load(f)
        assert record["pipeline_name"] == "TEST_PIPE"
        assert record["cron_exp"] == "*/5 * * * *"
        assert record["ok"] is True
        assert record["duration_ms"] == 2000
        assert len(record["executions"]) == 2

    def test_failed_record(self, history, history_dir):
        history.record("FAIL_PIPE", "0 * * * *", _make_result(ok=False, error="step2 failed"))
        files = os.listdir(history_dir)
        with open(os.path.join(history_dir, files[0])) as f:
            record = json.load(f)
        assert record["ok"] is False
        assert record["error"] == "step2 failed"


class TestGetHistory:

    def test_empty_history(self, history):
        assert history.get_history() == []

    def test_returns_records_newest_first(self, history):
        import time
        history.record("P1", "* * * * *", _make_result())
        time.sleep(0.01)
        history.record("P1", "* * * * *", _make_result())
        records = history.get_history()
        assert len(records) == 2
        assert records[0]["start_time"] >= records[1]["start_time"]

    def test_filter_by_pipeline(self, history):
        history.record("PIPE_A", "* * * * *", _make_result())
        history.record("PIPE_B", "* * * * *", _make_result())
        records = history.get_history(pipeline_name="PIPE_A")
        assert len(records) == 1
        assert records[0]["pipeline_name"] == "PIPE_A"

    def test_limit(self, history):
        for i in range(5):
            history.record("P", "* * * * *", _make_result())
        records = history.get_history(limit=2)
        assert len(records) == 2


class TestGetRecord:

    def test_get_existing_record(self, history, history_dir):
        history.record("DETAIL_PIPE", "0 9 * * *", _make_result())
        files = os.listdir(history_dir)
        record_id = files[0].replace(".json", "")
        record = history.get_record(record_id)
        assert record is not None
        assert record["pipeline_name"] == "DETAIL_PIPE"

    def test_get_nonexistent_record(self, history):
        assert history.get_record("NONEXISTENT_ID") is None


class TestCleanup:

    def test_removes_oldest_beyond_max(self, history, history_dir):
        import time
        for i in range(7):
            history.record(f"P_{i:02d}", "* * * * *", _make_result())
            time.sleep(0.01)
        files = os.listdir(history_dir)
        assert len(files) == 5  # max_records=5
