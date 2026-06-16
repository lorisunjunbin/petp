"""Unit tests for httpservice.HttpMetrics."""

import threading
import time
from unittest.mock import patch

import pytest

from httpservice.HttpMetrics import HttpMetrics


def test_record_start_end_counts():
    m = HttpMetrics(slow_threshold_ms=10_000, quantile_window=256)
    for _ in range(100):
        token = m.record_start("GET:/health")
        m.record_end(token, 200)
    snap = m.snapshot()
    stats = snap["endpoints"]["GET:/health"]
    assert stats["total"] == 100
    assert stats["success"] == 100
    assert stats["failed"] == 0
    assert stats["in_flight"] == 0


def test_failure_counted_on_5xx_or_exception():
    m = HttpMetrics()
    t1 = m.record_start("POST:/x")
    m.record_end(t1, 500)  # 5xx → failed
    t2 = m.record_start("POST:/x")
    m.record_end(t2, 200, exception=True)  # exception → failed
    t3 = m.record_start("POST:/x")
    m.record_end(t3, 200)  # success
    snap = m.snapshot()["endpoints"]["POST:/x"]
    assert snap["total"] == 3
    assert snap["failed"] == 2
    assert snap["success"] == 1


def test_quantiles_known_samples():
    m = HttpMetrics(slow_threshold_ms=10_000, quantile_window=300)
    # Inject samples by shorting record_start/end with mock time
    base = [0.0]
    def fake_perf():
        return base[0]
    with patch("httpservice.HttpMetrics.time.perf_counter", side_effect=fake_perf):
        for v in range(1, 257):  # 1..256 ms → samples in ms (since duration*1000)
            base[0] = 0.0
            token = m.record_start("GET:/q")
            base[0] = v / 1000.0  # delta seconds → v ms after *1000
            m.record_end(token, 200)
    snap = m.snapshot()["endpoints"]["GET:/q"]
    # Nearest-rank: idx = int(n*p). n=256, p=0.5 -> 128 -> samples[128]=129
    assert snap["p50_ms"] == pytest.approx(129.0, abs=2)
    # p95 -> int(256*0.95) = 243 -> samples[243]=244
    assert snap["p95_ms"] == pytest.approx(244.0, abs=2)
    # p99 -> int(256*0.99) = 253 -> samples[253]=254
    assert snap["p99_ms"] == pytest.approx(254.0, abs=2)


def test_concurrent_record_no_lost_updates():
    m = HttpMetrics(slow_threshold_ms=10_000, quantile_window=2048)
    n_threads = 8
    per_thread = 1000
    barrier = threading.Barrier(n_threads)

    def worker():
        barrier.wait()
        for _ in range(per_thread):
            t = m.record_start("POST:/concurrent")
            m.record_end(t, 200)

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    snap = m.snapshot()["endpoints"]["POST:/concurrent"]
    assert snap["total"] == n_threads * per_thread
    assert snap["success"] == n_threads * per_thread
    assert snap["in_flight"] == 0


def test_slow_log_threshold():
    m = HttpMetrics(slow_threshold_ms=100, quantile_window=10, slow_window=20)
    base = [0.0]
    def fake_perf():
        return base[0]
    with patch("httpservice.HttpMetrics.time.perf_counter", side_effect=fake_perf):
        # Fast request — must NOT enter slow_recent
        base[0] = 0.0
        t1 = m.record_start("GET:/fast")
        base[0] = 0.05  # 50 ms
        m.record_end(t1, 200)
        # Slow request — MUST enter slow_recent
        base[0] = 0.0
        t2 = m.record_start("POST:/slow")
        base[0] = 0.5  # 500 ms
        m.record_end(t2, 200)
    snap = m.snapshot()
    assert len(snap["slow_recent"]) == 1
    assert snap["slow_recent"][0]["endpoint"] == "POST:/slow"
    assert snap["slow_recent"][0]["duration_ms"] >= 100


def test_snapshot_top_level_fields():
    m = HttpMetrics()
    snap = m.snapshot()
    assert set(snap.keys()) == {"uptime_s", "ts", "endpoints", "executor", "slow_recent"}
    assert isinstance(snap["uptime_s"], float)
    assert isinstance(snap["ts"], int)
    assert isinstance(snap["endpoints"], dict)
    assert isinstance(snap["executor"], dict)
    assert isinstance(snap["slow_recent"], list)


def test_executor_introspection_failure_returns_negative():
    """A bogus executor (no _work_queue / _threads) must not raise; fields default to -1."""
    class FakeExecutor:
        _max_workers = 7
        # intentionally no _work_queue / _threads
    m = HttpMetrics(executor_provider=lambda: FakeExecutor())
    info = m.snapshot()["executor"]
    assert info["max_workers"] == 7
    assert info["queue_depth"] == -1
    assert info["active_workers"] == -1


def test_executor_introspection_no_provider():
    m = HttpMetrics()  # no executor_provider
    info = m.snapshot()["executor"]
    assert info == {"max_workers": -1, "active_workers": -1, "queue_depth": -1}


def test_record_end_unknown_token_is_safe():
    m = HttpMetrics()
    # token references endpoint that was never started — should not raise
    m.record_end(("GET:/never_started", time.perf_counter()), 200)
    # And None token is no-op
    m.record_end(None, 200)
