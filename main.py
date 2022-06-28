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

    def string(self):
        return 'https://static.tenki.jp/static-images/radar/{}/{}/{}/{}/{}/{}/pref-{}-large.jpg'.format(self.s_year(), self.s_month(), self.s_day(), self.s_hour(), self.s_minute(), '00', self.pref.id)
 
    def min_ago(self, min: int):
        if min % 5 != 0:
            raise Exception("minute is not a multiple of 5")
        return MapUrl(self.pref, self.now - datetime.timedelta(minutes=min))
    def min_ago_string(self, min: int):
        mg = self.min_ago(min)
        return mg.string()

class WeatherClient:
    def __init__(self, mapUrl: MapUrl, _dir_path: str):
        self.mapUrl = mapUrl
        self.dir_path = _dir_path
        self.maxretry = 10

    def build_file_name(self):
        return '{}-{}-{}-{}-{}-00-pref-{}.jpg'.format(self.mapUrl.s_year(), self.mapUrl.s_month(), self.mapUrl.s_day(), self.mapUrl.s_hour(), self.mapUrl.s_minute(), self.mapUrl.pref.id)
    def fetch_weathermap(self):
        challenge_url = self.mapUrl.string()
        ago = 0
        file_name = '{}-{}-{}-{}-{}-00-pref-{}.jpg'.format(self.mapUrl.s_year(), self.mapUrl.s_month(), self.mapUrl.s_day(), self.mapUrl.s_hour(), self.mapUrl.s_minute(), self.mapUrl.pref.id)
        for i in range(self.maxretry-1):
            try:
                with urllib.request.urlopen(challenge_url) as web_file:
                    weather_map = web_file.read()
                with open('{}{}'.format(self.dir_path, file_name), mode='wb') as local_file:
                    local_file.write(weather_map)
            except urllib.error.HTTPError as e:
                if i == range(self.maxretry-1):
                    raise
                else:
                    ago+=5
                    min_ago = self.mapUrl.min_ago(ago)
                    challenge_url = min_ago.string()
                    logger.debug(min_ago.s_minute())
                    file_name = '{}-{}-{}-{}-{}-00-pref-{}.jpg'.format(min_ago.s_year(), min_ago.s_month(), min_ago.s_day(), min_ago.s_hour(), min_ago.s_minute(), min_ago.pref.id)
                    logger.warning('retry')
            except urllib.error.URLError as e:
                logger.fatal(e)
                break

nowMap = MapUrl(Prefecture(_id=14, _name='埼玉'), datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST')))
wc = WeatherClient(nowMap, "data/")
wc.fetch_weathermap()