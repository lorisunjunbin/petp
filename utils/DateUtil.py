from datetime import datetime, timedelta


class DateUtil:

    @staticmethod
    def get_week_start_end(date):
        start_of_week = date - timedelta(days=date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0), end_of_week.replace(hour=23, minute=59,
                                                                                                     second=59,
                                                                                                     microsecond=999)

    @staticmethod
    def get_week_start_end_str(week_start, week_end, df="%d.%m.%Y", separator=' ~ '):
        return week_start.strftime(df) + separator + week_end.strftime(df)

    @staticmethod
    def get_week_start_end_with(date, delta):
        start_of_week = date - timedelta(days=date.weekday() - delta * 7)
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0), end_of_week.replace(hour=23, minute=59,
                                                                                                     second=59,
                                                                                                     microsecond=999)

    @staticmethod
    def get_date_with_delta(date, delta=0):
        return date + timedelta(days=delta)

    @staticmethod
    def get_week_num(date):
        return int(date.strftime("%U"))

    @staticmethod
    def get_date(date_str, df='%d.%m.%Y'):
        return datetime.strptime(date_str, df)

    @staticmethod
    def get_now():
        return datetime.now()

    @staticmethod
    def get_now_in_str(df="%Y%m%d%H%M%S"):
        return datetime.now().strftime(df)

    @staticmethod
    def get_date_str_with(date_str, delta, fromdf="%d.%m.%Y", todf="%d.%m.%Y"):
        given_date = DateUtil.get_date(date_str, fromdf)
        target_date = DateUtil.get_date_with_delta(given_date, delta)
        return target_date.strftime(todf)

    @staticmethod
    def remove_leading0(date_str, separator='-'):
        return separator.join(str(int(s)) for s in date_str.split(separator))

    @staticmethod
    def months_delta(date, month):
        return date + timedelta(months=month)

    @staticmethod
    def is_after_now(date):
        return date > DateUtil.get_now()
