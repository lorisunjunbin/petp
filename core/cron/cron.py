import logging
import threading
import time
from datetime import datetime, timedelta
from croniter import croniter
from core.cron.runnableascron import RunnAbleAsCron


class Cron:
    runnableAsCron: [RunnAbleAsCron] = []
    runningCron: {str} = set()

    def __init__(self, ):
        threading.Thread(target=self._loop_worker, daemon=True).start()

    def add_one(self, cron: RunnAbleAsCron):
        self.runnableAsCron.append(cron)

    def stop_one(self, cron: RunnAbleAsCron):
        key = cron.get_key()
        if key in self.runningCron:
            self.runningCron.remove(key)
            logging.info('Cron - stop cron: ' + key)

    def stop_all(self):
        self.runningCron.clear()
        logging.info('Cron - stop ALL')

    def _loop_worker(self):
        logging.info('cron - loop_worker is running')
        while True:
            if len(self.runnableAsCron) > 0:
                c: RunnAbleAsCron = self.runnableAsCron.pop(0)
                key = c.get_key()

                if not key in self.runningCron:
                    logging.info('Cron - start cron :' + key)
                    self.runningCron.add(key)
                    threading.Thread(target=self._check_and_run, args=(c,), daemon=True).start()
            else:
                time.sleep(5)

    def _get_running_key(self, pipeline: RunnAbleAsCron):
        return f'{pipeline.pipeline}_{pipeline.cronExp}'

    def _check_and_run(self, cron: RunnAbleAsCron):

        schedule = cron.get_cron()
        key = cron.get_key()
        nextRunTime = self._get_next_cron_run_time(schedule)
        logging.info(f'Cron - check_and_run {key} -> next run @{nextRunTime}')
        while True:
            if not key in self.runningCron:
                logging.info('Cron - Thread finished of cron: ' + key)
                break

            roundedDownTime = self._round_down_time()
            if (roundedDownTime == nextRunTime):
                logging.info(f'Cron - running_as_cron [ {schedule} ] start : {cron.get_name()}')
                cron.runsync({'running_as_cron': schedule})
                logging.info(f'Cron - running_as_cron [ {schedule} ] done: {cron.get_name()}')
                nextRunTime = self._get_next_cron_run_time(schedule)
            elif (roundedDownTime > nextRunTime):
                # We missed an execution. Error. Re initialize.
                nextRunTime = self._get_next_cron_run_time(schedule)
            self._sleep_till_top_of_next_minute()

    # Round time down to the top of the previous minute
    def _round_down_time(self, dt=None, dateDelta=timedelta(minutes=1)):
        roundTo = dateDelta.total_seconds()
        if dt == None: dt = datetime.now()
        seconds = (dt - dt.min).seconds
        rounding = (seconds + roundTo / 2) // roundTo * roundTo
        return dt + timedelta(0, rounding - seconds, -dt.microsecond)

    # Get next run time from now, based on schedule specified by cron string
    def _get_next_cron_run_time(self, schedule):
        return croniter(schedule, datetime.now()).get_next(datetime)

    # Sleep till the top of the next minute
    def _sleep_till_top_of_next_minute(self):
        t = datetime.utcnow()
        sleeptime = 60 - (t.second + t.microsecond / 1000000.0)
        time.sleep(sleeptime)
