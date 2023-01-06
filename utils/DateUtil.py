import locale
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from utils.OSUtils import OSUtils


class DateUtil:

    @staticmethod
    def get_week_start_end(date):
        start_of_week = date - timedelta(days=date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        week_start = start_of_week.replace(
            hour=0, minute=0, second=0, microsecond=0)
        week_end = end_of_week.replace(
            hour=23, minute=59, second=59, microsecond=999)

        return week_start, week_end

    @staticmethod
    def get_week_start_end_str(week_start, week_end, df="%d.%m.%Y", separator=' ~ '):
        return DateUtil._dt_strftime(week_start, df) + separator + DateUtil._dt_strftime(week_end, df)

    @staticmethod
    def get_week_start_end_with(date, delta):
        start_of_week = date - timedelta(days=date.weekday() - delta * 7)
        end_of_week = start_of_week + timedelta(days=6)

        week_start = start_of_week.replace(
            hour=0, minute=0, second=0, microsecond=0)
        week_end = end_of_week.replace(
            hour=23, minute=59, second=59, microsecond=999)

        return week_start, week_end

    @staticmethod
    def get_date_with_delta(date, delta=0):
        return date + timedelta(days=delta)

    @staticmethod
    def get_week_in_cw(date):
        return 'CW' + str(DateUtil.get_week_num(date))

    @staticmethod
    def get_week_num(date):
        return int(DateUtil._dt_strftime(date, "%U"))

    @staticmethod
    def setLocale():
        if OSUtils.get_sytem() == 'win32':
            locale.setlocale(locale.LC_ALL, 'en-US.UTF-8')  # for windows
        else:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  # for mac os, or others.

    @staticmethod
    def get_date(date_str, df='%d.%m.%Y'):
        return DateUtil._dt_strptime(date_str, df)

    @staticmethod
    def get_now():
        return datetime.now()

    @staticmethod
    def get_now_in_str(df="%Y%m%d%H%M%S"):
        return DateUtil._dt_strftime(datetime.now(), df)

    @staticmethod
    def get_date_str_with(date_str, delta, fromdf="%d.%m.%Y", todf="%d.%m.%Y"):
        given_date = DateUtil.get_date(date_str, fromdf)
        target_date = DateUtil.get_date_with_delta(given_date, delta)
        return DateUtil._dt_strftime(target_date, todf)

    @staticmethod
    def remove_leading0(date_str, separator='-'):
        arr = date_str.split(separator)
        target_arr = []
        for s in arr:
            target_arr.append(str(int(s)))
        return separator.join(target_arr)

    @staticmethod
    def _dt_strftime(d, df) -> str:
        DateUtil.setLocale()
        return d.strftime(df)

    @staticmethod
    def _dt_strptime(dstr, df):
        DateUtil.setLocale()
        return datetime.strptime(dstr, df)

    @staticmethod
    def months_delta(date, month):
        return date + relativedelta(months=month)

    @staticmethod
    def is_after_now(date):
        return date > DateUtil.get_now()
