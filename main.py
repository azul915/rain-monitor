from calendar import month
import datetime
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


class Prefecture:
    def __init__(self, _id: int, _name: str):
        self.id = _id
        self.name = _name

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
    def syaer(self):
        return str(self.now.year)
    def smonth(self):
        return format(self.month(), '02')
    def sday(self):
        return format(self.day(), '02')
    def shour(self):
        return format(self.hour(), '02')
    def sminute(self):
        return format(self.la_minute(), '02')

    def string(self):
        return 'https://static.tenki.jp/static-images/radar/{}/{}/{}/{}/{}/{}/pref-{}-large.jpg'.format(self.syaer(), self.smonth(), self.sday(), self.shour(), self.sminute(), '00', self.pref.id)
 
    def min_ago_string(self, min: int):
        if min % 5 != 0:
            raise Exception("minuteが5の倍数でない")
        ma = self.now - datetime.timedelta(minutes=min)
        year = str(ma.year)
        la_minute = int(ma.minute) - int(ma.minute % 5)
        month, day, hour, minute = list(map(lambda x: format(x, '02'), list(map(lambda x: int(x), [ma.month, ma.day, ma.hour, la_minute]))))
        return 'https://static.tenki.jp/static-images/radar/{}/{}/{}/{}/{}/{}/pref-{}-large.jpg'.format(year, month, day, hour, minute, '00', self.pref.id)

class WeatherClient:
    def __init__(self, mapUrl: MapUrl, _dst_path: str):
        self.mapUrl = mapUrl
        self.dst_path = _dst_path
        self.maxretry = 10

    def fetch_weathermap(self):
        challenge_url = self.mapUrl.string()
        ago = 0
        for i in range(self.maxretry-1):
            try:
                with urllib.request.urlopen(challenge_url) as web_file:
                    weather_map = web_file.read()
                with open(self.dst_path, mode='wb') as local_file:
                    local_file.write(weather_map)
            except urllib.error.HTTPError as e:
                if i == range(self.maxretry-1):
                    raise
                else:
                    ago+=5
                    challenge_url = self.mapUrl.min_ago_string(ago)
                    logger.warning('retry')
            except urllib.error.URLError as e:
                logger.fatal(e)
                break

nowMap = MapUrl(Prefecture(_id=14, _name='埼玉'), datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST')))
wc = WeatherClient(nowMap, "data/pref-14-large.jpg")
wc.fetch_weathermap()