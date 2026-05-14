import datetime
import json
import logging

import cnlunar

from core.processor import Processor


class CNLunarProcessor(Processor):
    TPL: str = '{"date":"","data_key":"almanac"}'

    DESC: str = '''
        Get Chinese almanac (黄历) information for a given date using cnlunar library.

        Returns a dict with: date, lunar, ganzhi, zodiac, solar_term, yi, ji.

        - date: Date string in YYYY-MM-DD format; empty means today (supports expression, default: "")
        - data_key: Key in data_chain to store the result dict (supports expression, default: "almanac")
    '''

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        date_str = self.expression2str(self.get_param('date'))
        data_key = self.expression2str(self.get_param('data_key'))

        if date_str and not date_str.startswith('{'):
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        else:
            date = datetime.datetime.now()

        a = cnlunar.Lunar(date)
        month_cn = a.lunarMonthCn.replace('大', '').replace('小', '')
        result = {
            "date": date.strftime("%Y-%m-%d"),
            "lunar": a.lunarYearCn + month_cn + a.lunarDayCn,
            "ganzhi": a.year8Char + '年 ' + a.month8Char + '月 ' + a.day8Char + '日',
            "zodiac": a.chineseYearZodiac,
            "solar_term": a.todaySolarTerms if a.todaySolarTerms != "无" else "",
            "yi": "、".join(a.goodThing) if a.goodThing else "",
            "ji": "、".join(a.badThing) if a.badThing else "",
        }

        logging.info('[CNLunar] %s → %s %s', result['date'], result['lunar'], result['ganzhi'])
        self.populate_data(data_key, result)
