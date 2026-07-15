import logging
import threading
import time
import traceback
from datetime import datetime
from croniter import croniter
from core.cron.runnableascron import RunnableAsCron

from threading import Condition, Thread


class Cron:

    def __init__(self, view, on_run=None, on_record=None, max_consecutive_failures: int = 5):
        """
        :param view: wxPython view (None in BG mode)
        :param on_run: optional callback (cron_obj, init_data) -> result_dict.
                      If None, falls back to cron.run_sync() which returns None.
        :param on_record: optional callback (pipeline_name, cron_exp, result_dict) -> None
                          for persisting cron run history. Called for both success and failure.
        :param max_consecutive_failures: circuit-breaker threshold. After this many consecutive
                                          failures, the pipeline is suspended and stops being
                                          scheduled until manually restarted (stop_one + add_one).
                                          Set to 0 to disable the breaker entirely.
        """
        self.view = view
        self._on_run = on_run
        self._on_record = on_record
        self._max_consecutive_failures = max(0, int(max_consecutive_failures))
        self._pending: list[RunnableAsCron] = []
        self._running_keys: set[str] = set()
        self._running_crons: dict[str, RunnableAsCron] = {}
        self._threads: dict[str, Thread] = {}
        self._stop_events: dict[str, threading.Event] = {}
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._has_work = threading.Event()
        # Circuit breaker state — keyed by pipeline name (NOT cron key, so re-add resets cleanly).
        self._consecutive_failures: dict[str, int] = {}
        self._suspended_until_restart: set[str] = set()
        self._last_status: dict[str, str] = {}      # 'ok' | 'error'
        self._last_error: dict[str, str] = {}
        self._worker = Thread(target=self._loop_worker, daemon=True)
        self._worker.start()

    def add_one(self, cron: RunnableAsCron):
        key = cron.get_key()
        name = cron.get_name()
        with self._lock:
            if key in self._running_keys:
                logging.info('Cron - already running: %s, skip', key)
                return
            if any(c.get_key() == key for c in self._pending):
                logging.info('Cron - already pending: %s, skip', key)
                return
            # Manual re-add resets circuit breaker for this pipeline.
            self._consecutive_failures.pop(name, None)
            self._suspended_until_restart.discard(name)
            self._pending.append(cron)
        self._has_work.set()

    def stop_one(self, cron: RunnableAsCron):
        key = cron.get_key()
        name = cron.get_name()
        with self._lock:
            self._running_keys.discard(key)
            self._running_crons.pop(key, None)
            self._pending[:] = [c for c in self._pending if c.get_key() != key]
            t = self._threads.pop(key, None)
            evt = self._stop_events.pop(key, None)
            self._suspended_until_restart.discard(name)
            self._consecutive_failures.pop(name, None)
        if evt:
            evt.set()
        logging.info('Cron - stop cron: %s', key)
        if t is not None:
            t.join(timeout=5)

    def stop_all(self):
        self._stop.set()
        with self._lock:
            self._running_keys.clear()
            self._running_crons.clear()
            self._pending.clear()
            threads = list(self._threads.values())
            self._threads.clear()
            for evt in self._stop_events.values():
                evt.set()
            self._stop_events.clear()
            self._suspended_until_restart.clear()
            self._consecutive_failures.clear()
        self._has_work.set()
        for t in threads:
            t.join(timeout=5)
        self._worker.join(timeout=3)
        logging.info('Cron - stop ALL')

    def get_running_info(self) -> list[dict]:
        with self._lock:
            keys = list(self._running_keys)
            pending_keys = [c.get_key() for c in self._pending]
            failures_snapshot = dict(self._consecutive_failures)
            suspended_snapshot = set(self._suspended_until_restart)
            last_status_snapshot = dict(self._last_status)
            last_error_snapshot = dict(self._last_error)
        result = []
        for key in keys:
            info = {"pipeline_name": key, "status": "running"}
            try:
                cron_obj = self._get_cron_obj_by_key(key)
                if cron_obj:
                    name = cron_obj.get_name()
                    info["cron_exp"] = cron_obj.get_cron()
                    info["cron_desc"] = getattr(cron_obj, 'cronDesc', '')
                    info["next_run"] = self._get_next_cron_run_time(cron_obj.get_cron()).isoformat(timespec="seconds")
                    info["consecutive_failures"] = failures_snapshot.get(name, 0)
                    info["last_status"] = last_status_snapshot.get(name, "")
                    if name in last_error_snapshot:
                        info["last_error"] = last_error_snapshot[name]
                    if name in suspended_snapshot:
                        info["status"] = "suspended"
                        info["next_run"] = None
            except Exception:
                pass
            result.append(info)
        for key in pending_keys:
            result.append({"pipeline_name": key, "status": "pending"})
        return result

    def _get_cron_obj_by_key(self, key: str):
        with self._lock:
            if key in self._running_crons:
                return self._running_crons[key]
            for c in self._pending:
                if c.get_key() == key:
                    return c
        return None

    def _loop_worker(self):
        logging.info('cron - loop_worker is running')
        while not self._stop.is_set():
            self._has_work.wait()
            if self._stop.is_set():
                break
            with self._lock:
                if not self._pending:
                    self._has_work.clear()
                    continue
                c = self._pending.pop(0)
                key = c.get_key()
                if key in self._running_keys:
                    continue
                self._running_keys.add(key)
                self._running_crons[key] = c
                stop_evt = threading.Event()
                self._stop_events[key] = stop_evt
                if not self._pending:
                    self._has_work.clear()
            logging.info('Cron - start cron: %s', key)
            t = Thread(target=self._check_and_run, args=(c, stop_evt), daemon=True)
            with self._lock:
                self._threads[key] = t
            t.start()

    def _check_and_run(self, cron: RunnableAsCron, stop_evt: threading.Event):
        schedule = cron.get_cron()
        key = cron.get_key()
        name = cron.get_name()
        cond = Condition()
        nextRunTime = self._get_next_cron_run_time(schedule)
        logging.info('Cron - check_and_run %s -> next run @%s', key, nextRunTime)
        while not self._stop.is_set() and not stop_evt.is_set():
            if key not in self._running_keys:
                logging.info('Cron - Thread finished of cron: %s', key)
                break

            # Skip firing entirely if breaker is open. Stay in the loop so that
            # stop_one() / restart can still terminate or revive the thread.
            with self._lock:
                is_suspended = name in self._suspended_until_restart

            roundedDownTime = self._round_down_time()
            if not is_suspended and roundedDownTime == nextRunTime:
                logging.info('Cron - running_as_cron [ %s ] start : %s', schedule, name)
                started = time.time()
                ok = False
                error_msg = None
                run_result = None
                try:
                    if self._on_run is not None:
                        run_result = self._on_run(cron, {'running_as_cron': schedule})
                    else:
                        cron.run_sync({'running_as_cron': schedule}, self.view, cond)
                    # If on_run returned a structured result, trust its ok flag.
                    if isinstance(run_result, dict) and 'ok' in run_result:
                        ok = bool(run_result['ok'])
                        error_msg = run_result.get('error')
                    else:
                        ok = True
                except Exception as e:
                    error_msg = repr(e)
                    logging.exception('Cron - exception in cron [ %s ] %s, will retry next schedule', schedule, name)

                self._post_run_update(name, schedule, started, ok, error_msg, run_result, cron)
                logging.info('Cron - running_as_cron [ %s ] done: %s (ok=%s)', schedule, name, ok)
                nextRunTime = self._get_next_cron_run_time(schedule)
            elif roundedDownTime > nextRunTime:
                nextRunTime = self._get_next_cron_run_time(schedule)
            if stop_evt.wait(timeout=self._seconds_till_next_minute()):
                break
        with self._lock:
            self._running_keys.discard(key)
            self._threads.pop(key, None)
            self._running_crons.pop(key, None)
            self._stop_events.pop(key, None)

    def _post_run_update(self, name: str, schedule: str, started: float,
                          ok: bool, error_msg, run_result, cron_obj):
        """Update breaker state, emit history record."""
        # Breaker bookkeeping
        with self._lock:
            if ok:
                self._consecutive_failures.pop(name, None)
                self._last_status[name] = 'ok'
                self._last_error.pop(name, None)
            else:
                self._consecutive_failures[name] = self._consecutive_failures.get(name, 0) + 1
                self._last_status[name] = 'error'
                if error_msg:
                    self._last_error[name] = str(error_msg)[:500]
                if (self._max_consecutive_failures > 0 and
                        self._consecutive_failures[name] >= self._max_consecutive_failures):
                    self._suspended_until_restart.add(name)
                    logging.error(
                        'Cron - SUSPENDED pipeline %s after %d consecutive failures (last error: %s)',
                        name, self._consecutive_failures[name], error_msg,
                    )

        # History record — pass through if caller supplied a structured result,
        # otherwise synthesize a minimal one so GUI runs are tracked too.
        if self._on_record is None:
            return
        try:
            if isinstance(run_result, dict) and 'ok' in run_result:
                record_payload = run_result
            else:
                duration_ms = int((time.time() - started) * 1000)
                record_payload = {
                    'ok': ok,
                    'error': error_msg if not ok else None,
                    'data': {},
                    'meta': {
                        'duration_ms': duration_ms,
                        'executions': [],
                    },
                }
                if not ok and error_msg:
                    record_payload['meta']['traceback'] = traceback.format_exc()
            self._on_record(name, schedule, record_payload)
        except Exception:
            logging.exception('Cron - on_record callback failed for %s', name)

    @staticmethod
    def _round_down_time(dt=None):
        if dt is None:
            dt = datetime.now()
        return dt.replace(second=0, microsecond=0)

    # Get next run time from now, based on schedule specified by cron string
    def _get_next_cron_run_time(self, schedule):
        return croniter(schedule, datetime.now()).get_next(datetime)

    @staticmethod
    def _seconds_till_next_minute():
        t = datetime.now()
        return 60 - (t.second + t.microsecond / 1_000_000.0)
