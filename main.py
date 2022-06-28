from calendar import month
import datetime
import os
import urllib.error
import urllib.request
from logging import getLogger, StreamHandler, DEBUG, Formatter
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
formatter = Formatter('%(levelname)s  %(asctime)s  [%(name)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False

class CurrentTime:
    def __init__(self, ct: datetime.datetime):
        self.value = ct

class Prefecture:
    def __init__(self, _id: str, _number: int, _disp_name: str):
        self.id = _id
        self.number = _number
        self.disp_name = _disp_name

class MapUrl:
    def __init__(self, _pref: Prefecture, _now: datetime.datetime):
        self.pref = _pref
        self.now = _now
    def year(self):
        return int(self.now.year)
    def month(self):
        return int(self.now.month)
    def day(self):
        return int(self.now.day)
    def hour(self):
        return int(self.now.hour)
    def la_minute(self):
        return int(self.now.minute) - int(self.now.minute) % 5
    def s_year(self):
        return str(self.now.year)
    def s_month(self):
        return format(self.month(), '02')
    def s_day(self):
        return format(self.day(), '02')
    def s_hour(self):
        return format(self.hour(), '02')
    def s_minute(self):
        return format(self.la_minute(), '02')

    def now_string(self):
        return 'https://static.tenki.jp/static-images/radar/{}/{}/{}/{}/{}/{}/pref-{}-large.jpg'.format(self.s_year(), self.s_month(), self.s_day(), self.s_hour(), self.s_minute(), '00', self.pref.number)
 
    def min_ago(self, min: int):
        if min % 5 != 0:
            raise Exception("minute is not a multiple of 5")
        return MapUrl(self.pref, self.now - datetime.timedelta(minutes=min))

class LocalImage:
    def __init__(self, mu: MapUrl, _created_at: datetime.datetime):
        self.name = '{}-{}-{}-{}-{}-00-pref-{}.jpg'.format(mu.s_year(), mu.s_month(), mu.s_day(), mu.s_hour(), mu.s_minute(), mu.pref.number)
        self.created_at = mu.now

    def created_at_str(self):
        return str(self.created_at)

class WeatherClient:
    def __init__(self, mapUrl: MapUrl, _dir_path: str):
        self.mapUrl = mapUrl
        self.dir_path = _dir_path
        self.maxretry = 10

    def path_to_file(self, li: LocalImage):
        return '{}{}'.format(self.dir_path, li.name)

    def fetch_weathermap(self):
        u = self.mapUrl.now_string()
        li = LocalImage(self.mapUrl, datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST')))
        ago = 0
        for i in range(self.maxretry-1):
            try:
                with urllib.request.urlopen(u) as web_file:
                    weather_map = web_file.read()
                    if os.path.isfile(self.path_to_file(li)):
                        os.remove(self.path_to_file(li))
                with open(self.path_to_file(li), mode='wb') as local_file:
                    local_file.write(weather_map)
            except urllib.error.HTTPError as e:
                if i == range(self.maxretry-1):
                    raise
                else:
                    ago+=5
                    min_ago = self.mapUrl.min_ago(ago)
                    u = min_ago.now_string()
                    logger.debug(min_ago.s_minute())
                    li = LocalImage(min_ago, datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST')))
                    logger.warning('retry')
            except urllib.error.URLError as e:
                logger.fatal(e)
                break

prefectures: list[Prefecture] = [
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

    nowMap = MapUrl(target_prefecture, datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST')))

    wc = WeatherClient(nowMap, 'data/')
    wc.fetch_weathermap()
