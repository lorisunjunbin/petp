"""HTTP request metrics aggregator for the BG/Docker server.

In-memory, zero external dependencies. Exposed via ``GET /petp/metrics`` and
periodically logged with the ``METRICS `` prefix.
"""

import threading
import time
from collections import deque
from typing import Any, Callable, Optional


class _EndpointStats:
    """Per-endpoint counters, sample buffer, and a dedicated lock.

    A per-endpoint lock keeps the critical section microscopic and avoids
    contention between unrelated endpoints under concurrent load.
    """

    __slots__ = (
        "total", "success", "failed", "in_flight",
        "last_called_at", "total_duration_ms",
        "samples", "lock",
    )

    def __init__(self, window: int):
        self.total: int = 0
        self.success: int = 0
        self.failed: int = 0
        self.in_flight: int = 0
        self.last_called_at: float = 0.0
        self.total_duration_ms: float = 0.0
        self.samples: deque = deque(maxlen=window)
        self.lock: threading.Lock = threading.Lock()


class HttpMetrics:
    """Aggregate HTTP request metrics for the BG server.

    Public surface:
      - ``record_start(endpoint)``        called when a request enters dispatch
      - ``record_end(token, status_code, exception=False)``  called when it leaves
      - ``snapshot()``                    serialisable dict for /petp/metrics + log

    Layout:
      - ``_endpoints[endpoint] = _EndpointStats``  (per-endpoint lock)
      - ``_slow``                                    recent slow requests (deque)
      - ``_lock``                                    global lock for dict/slow writes
    """

    def __init__(
        self,
        slow_threshold_ms: int = 5000,
        quantile_window: int = 256,
        slow_window: int = 20,
        executor_provider: Optional[Callable[[], Any]] = None,
    ):
        self._started_at: float = time.perf_counter()
        self._endpoints: dict[str, _EndpointStats] = {}
        self._slow: deque = deque(maxlen=slow_window)
        self._lock: threading.Lock = threading.Lock()
        self._slow_threshold_ms: int = int(slow_threshold_ms)
        self._quantile_window: int = int(quantile_window)
        self._executor_provider = executor_provider

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_start(self, endpoint: str) -> tuple:
        """Mark the start of a request. Returns a token to pass to ``record_end``."""
        stats = self._get_or_create(endpoint)
        with stats.lock:
            stats.total += 1
            stats.in_flight += 1
            stats.last_called_at = time.time()
        return (endpoint, time.perf_counter())

    def record_end(self, token: tuple, status_code: int, exception: bool = False) -> None:
        if token is None:
            return
        endpoint, t0 = token
        duration_ms = (time.perf_counter() - t0) * 1000.0

        stats = self._endpoints.get(endpoint)
        if stats is None:
            # record_start was skipped or endpoint disappeared — no-op
            return

        is_failure = exception or (isinstance(status_code, int) and status_code >= 500)
        with stats.lock:
            stats.in_flight = max(0, stats.in_flight - 1)
            stats.total_duration_ms += duration_ms
            stats.samples.append(duration_ms)
            if is_failure:
                stats.failed += 1
            else:
                stats.success += 1

        if duration_ms >= self._slow_threshold_ms:
            with self._lock:
                self._slow.append({
                    "endpoint": endpoint,
                    "duration_ms": round(duration_ms, 1),
                    "status": int(status_code) if isinstance(status_code, int) else 0,
                    "ts": int(time.time()),
                })

    def _get_or_create(self, endpoint: str) -> _EndpointStats:
        # Fast path: endpoint already known, no lock needed (dict reads are atomic)
        stats = self._endpoints.get(endpoint)
        if stats is not None:
            return stats
        # Slow path: create under global lock (double-checked)
        with self._lock:
            stats = self._endpoints.get(endpoint)
            if stats is None:
                stats = _EndpointStats(self._quantile_window)
                self._endpoints[endpoint] = stats
            return stats

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> dict:
        """Return a serialisable snapshot of the current metrics state."""
        endpoints_out: dict[str, dict] = {}
        # Take a fast copy under each per-endpoint lock, release before sorting
        for endpoint, stats in list(self._endpoints.items()):
            with stats.lock:
                total = stats.total
                success = stats.success
                failed = stats.failed
                in_flight = stats.in_flight
                last_called_at = stats.last_called_at
                total_duration_ms = stats.total_duration_ms
                samples_copy = list(stats.samples)
            avg_ms = (total_duration_ms / success) if success > 0 else 0.0
            p50, p95, p99 = self._compute_quantiles(samples_copy)
            endpoints_out[endpoint] = {
                "total": total,
                "success": success,
                "failed": failed,
                "in_flight": in_flight,
                "last_called_at": round(last_called_at, 3) if last_called_at else 0,
                "avg_ms": round(avg_ms, 2),
                "p50_ms": round(p50, 2),
                "p95_ms": round(p95, 2),
                "p99_ms": round(p99, 2),
            }

        with self._lock:
            slow_copy = list(self._slow)

        return {
            "uptime_s": round(time.perf_counter() - self._started_at, 1),
            "ts": int(time.time()),
            "endpoints": endpoints_out,
            "executor": self._executor_introspect(),
            "slow_recent": slow_copy,
        }

    @staticmethod
    def _compute_quantiles(samples: list) -> tuple:
        n = len(samples)
        if n == 0:
            return (0.0, 0.0, 0.0)
        s = sorted(samples)
        # Nearest-rank, clamped to last index for n>=1
        def at(p: float) -> float:
            idx = int(n * p)
            if idx >= n:
                idx = n - 1
            return s[idx]
        return (at(0.5), at(0.95), at(0.99))

    def _executor_introspect(self) -> dict:
        out = {"max_workers": -1, "active_workers": -1, "queue_depth": -1}
        if self._executor_provider is None:
            return out
        try:
            ex = self._executor_provider()
        except Exception:
            return out
        if ex is None:
            return out
        try:
            out["max_workers"] = int(getattr(ex, "_max_workers", -1))
        except Exception:
            pass
        try:
            out["queue_depth"] = ex._work_queue.qsize()
        except Exception:
            pass
        try:
            out["active_workers"] = sum(1 for t in ex._threads if t.is_alive())
        except Exception:
            pass
        return out
