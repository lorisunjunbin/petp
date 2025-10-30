import logging

from core.processor import Processor
from datetime import datetime, timedelta


class STOPPERProcessor(Processor):
    TPL: str = '{"stop_after":"2025-12-31 23:59:59", "stop_in_minutes":"0"}'

    DESC: str = f''' 
        stop after datetime - Once run through this process, will check current time whether after stop_after, if yes, then stop the execution.
        stop in minutes - Once run through this process, will check whether the execution has run for more than the given minutes, if yes, then stop the execution.
        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_GUI

    def process(self):
        stop_after = self.expression2str(self.get_param('stop_after'))
        now = datetime.now()
        logging.info(f"Current time: {now} will stop after: {stop_after}")
        # stop after datetime
        stop_after_dt = datetime.strptime(stop_after, '%Y-%m-%d %H:%M:%S')
        if now > stop_after_dt:
            self.execution.set_should_be_stop(True)
            logging.info(f"Current time {now} is after stop_after {stop_after_dt}, stopping execution.")
            return

        # stop in minutes
        stop_in_minutes = self.expression2str(self.get_param('stop_in_minutes'))
        if stop_in_minutes.isdigit() and int(stop_in_minutes) > 0:
            in_minutes = int(stop_in_minutes)
            stop_time = self.execution.get_run_at() + timedelta(minutes=in_minutes)
            logging.info(f"Current time: {now} will stop in {in_minutes} minutes, calculated stop time: {stop_time}")
            if now > stop_time:
                self.execution.set_should_be_stop(True)
                logging.info(f"Current time {now} is after stop time {stop_time}, stopping execution.")