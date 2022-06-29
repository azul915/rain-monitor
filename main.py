from calendar import month
import datetime
import os
import urllib.error
import urllib.request
from logging import getLogger, StreamHandler, DEBUG, Formatter, setLogRecordFactory
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
formatter = Formatter('%(levelname)s  %(asctime)s  [%(name)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False

class Minute:
    def __init__(self, dt: datetime.datetime):
        self.dt = dt - datetime.timedelta(minutes=dt.minute % 5)
        self.value = self.dt.minute
        self.str_value = str(self.value)
    def last_multiple_of_five(self):
        five_min_ago = self.value - datetime.timedelta(minutes=5)
        return five_min_ago.minute - five_min_ago.minute % 5
    def string(self):
        return self.str_value

class CurrentTime:
    def __init__(self, ct: datetime.datetime, _minute: Minute):
        self.value = _minute.dt
        self.minute = _minute
    def s_year(self):
        return str(self.value.year)
    def s_month(self):
        return format(self.value.month, '02')
    def s_day(self):
        return format(self.value.day, '02')
    def s_hour(self):
        return format(self.value.hour, '02')
    def s_minute(self):
        return format(self.minute.value, '02')
    def last_multiple_of_five(self):
        return self.value

class Prefecture:
    def __init__(self, _id: str, _number: int, _disp_name: str):
        self.id = _id
        self.number = _number
        self.disp_name = _disp_name
    def num(self):
        return self.number

class WeatherMapUrl:
    def __init__(self, ct: CurrentTime, pref: Prefecture):
        self.cur_time = ct
        self.pref = pref

class CurrentWeatherMapUrl(WeatherMapUrl):
    def __init__(self, ct: CurrentTime, pref: Prefecture):
        super().__init__(ct, pref)
        self.value = 'https://static.tenki.jp/static-images/radar/{}/{}/{}/{}/{}/00/pref-{}-large.jpg'.format(ct.s_year(), ct.s_month(), ct.s_day(), ct.s_hour(), ct.s_minute(), pref.num())
    def value(self):
        return self.value

class LocalImage:
    def __init__(self, ct: CurrentTime, pref: Prefecture):
        self.name = '{}-{}-{}-{}-{}-00-pref-{}.jpg'.format(ct.s_year(), ct.s_month(), ct.s_day(), ct.s_day(), ct.s_minute(), pref.num())
        self.created_at = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST'))
    def created_at_str(self):
        return str(self.created_at)

class WeatherClient:
    def __init__(self, pref: Prefecture, cur: CurrentTime, _max_retry: int, _dir_path: str):
        self.pref = pref
        self.cur_time = cur
        self.max_retry = _max_retry
        self.dir_path = _dir_path
    def path_to_file(self, local_image: LocalImage):
        return self.dir_path + local_image.name
    def fetch_map(self):
        li = LocalImage(self.cur_time, self.pref)
        cwmu = CurrentWeatherMapUrl(self.cur_time, self.pref)
        for i in range(self.max_retry-1):
            try:
                logger.debug(cwmu.value)
                with urllib.request.urlopen(cwmu.value) as web_file:
                    weather_map = web_file.read()
                    if os.path.isfile(self.path_to_file(li)):
                        os.remove(self.path_to_file(li))
                with open(self.path_to_file(li), mode='wb') as local_file:
                    local_file.write(weather_map)
            except urllib.error.HTTPError as e:
                if i == range(self.maxretry-1):
                    raise
                else:
                    five_minute_ago = cwmu.cur_time.last_multiple_of_five()
                    cwmu = CurrentWeatherMapUrl(five_minute_ago, self.pref)
                    logger.warning('retry')
            except urllib.error.URLError as e:
                logger.fatal(e)
                break

prefectures = [
    Prefecture(_id = 'aomori', _number = 5, _disp_name = '青森'),
    Prefecture(_id = 'iwate', _number = 6, _disp_name = '岩手'),
    Prefecture(_id = 'saitama', _number = 14, _disp_name = '埼玉'),
    Prefecture(_id = 'tokyo', _number = 16, _disp_name = '東京'),
    Prefecture(_id = 'okinawa', _number = 50, _disp_name = '沖縄')
]

if __name__ == '__main__':
    if os.getenv('PREF') == None:
        os.environ['PREF'] = 'saitama'

    target_prefecture = list(filter(lambda x: x.id == os.getenv('PREF'), prefectures))[0]

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST'))
    current_time = CurrentTime(now, Minute(now))
    logger.debug(now)
    logger.debug(current_time.value)
    wc = WeatherClient(target_prefecture, current_time, _max_retry = 5, _dir_path = 'data/')
    wc.fetch_map()