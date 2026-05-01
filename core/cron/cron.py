import logging
import threading
from datetime import datetime, timedelta
from croniter import croniter
from core.cron.runnableascron import RunnableAsCron

from threading import Condition, Thread


class Cron:

    def __init__(self, view, on_run=None):
        self.view = view
        self._on_run = on_run
        self._pending: list[RunnableAsCron] = []
        self._running_keys: set[str] = set()
        self._running_crons: dict[str, RunnableAsCron] = {}
        self._threads: dict[str, Thread] = {}
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._has_work = threading.Event()
        self._worker = Thread(target=self._loop_worker, daemon=True)
        self._worker.start()

    def add_one(self, cron: RunnableAsCron):
        key = cron.get_key()
        with self._lock:
            if key in self._running_keys:
                logging.info('Cron - already running: %s, skip', key)
                return
            if any(c.get_key() == key for c in self._pending):
                logging.info('Cron - already pending: %s, skip', key)
                return
            self._pending.append(cron)
        self._has_work.set()

    def stop_one(self, cron: RunnableAsCron):
        key = cron.get_key()
        with self._lock:
            self._running_keys.discard(key)
            self._running_crons.pop(key, None)
            self._pending[:] = [c for c in self._pending if c.get_key() != key]
            t = self._threads.pop(key, None)
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
        self._has_work.set()
        for t in threads:
            t.join(timeout=5)
        self._worker.join(timeout=3)
        logging.info('Cron - stop ALL')

    def get_running_info(self) -> list[dict]:
        with self._lock:
            keys = list(self._running_keys)
            pending_keys = [c.get_key() for c in self._pending]
        result = []
        for key in keys:
            info = {"pipeline_name": key, "status": "running"}
            try:
                cron_obj = self._get_cron_obj_by_key(key)
                if cron_obj:
                    info["cron_exp"] = cron_obj.get_cron()
                    info["cron_desc"] = getattr(cron_obj, 'cronDesc', '')
                    info["next_run"] = self._get_next_cron_run_time(cron_obj.get_cron()).isoformat(timespec="seconds")
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
                if not self._pending:
                    self._has_work.clear()
            logging.info('Cron - start cron: %s', key)
            t = Thread(target=self._check_and_run, args=(c,), daemon=True)
            with self._lock:
                self._threads[key] = t
            t.start()

    def _check_and_run(self, cron: RunnableAsCron):
        schedule = cron.get_cron()
        key = cron.get_key()
        cond = Condition()
        nextRunTime = self._get_next_cron_run_time(schedule)
        logging.info('Cron - check_and_run %s -> next run @%s', key, nextRunTime)
        while not self._stop.is_set():
            if key not in self._running_keys:
                logging.info('Cron - Thread finished of cron: %s', key)
                break

            roundedDownTime = self._round_down_time()
            if roundedDownTime == nextRunTime:
                logging.info('Cron - running_as_cron [ %s ] start : %s', schedule, cron.get_name())
                try:
                    if self._on_run is not None:
                        self._on_run(cron, {'running_as_cron': schedule})
                    else:
                        cron.run_sync({'running_as_cron': schedule}, self.view, cond)
                except Exception:
                    logging.exception('Cron - exception in cron [ %s ] %s, will retry next schedule', schedule, cron.get_name())
                logging.info('Cron - running_as_cron [ %s ] done: %s', schedule, cron.get_name())
                nextRunTime = self._get_next_cron_run_time(schedule)
            elif roundedDownTime > nextRunTime:
                nextRunTime = self._get_next_cron_run_time(schedule)
            if self._stop.wait(timeout=self._seconds_till_next_minute()):
                break
        with self._lock:
            self._threads.pop(key, None)
            self._running_crons.pop(key, None)

    # Round time down to the top of the previous minute
    def _round_down_time(self, dt=None, dateDelta=timedelta(minutes=1)):
        roundTo = dateDelta.total_seconds()
        if dt is None:
            dt = datetime.now()
        seconds = (dt - dt.min).seconds
        rounding = (seconds + roundTo / 2) // roundTo * roundTo
        return dt + timedelta(0, rounding - seconds, -dt.microsecond)

    # Get next run time from now, based on schedule specified by cron string
    def _get_next_cron_run_time(self, schedule):
        return croniter(schedule, datetime.now()).get_next(datetime)

    @staticmethod
    def _seconds_till_next_minute():
        t = datetime.now()
        return 60 - (t.second + t.microsecond / 1_000_000.0)
