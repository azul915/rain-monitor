import urllib.error
import urllib.request

class WeatherClient:
    def __init__(self, _url, _dst_path):
        self.url = _url
        self.dst_path = _dst_path

    def fetch_wethermap(self):
        try:
            with urllib.request.urlopen(self.url) as web_file:
                weather_map = web_file.read()
            with open(self.dst_path, mode='wb') as local_file:
                byte = local_file.write(weather_map)
                return byte > 0
        except urllib.error.URLError as e:
            print(e)
            return False

wc = WeatherClient("https://static.tenki.jp/static-images/radar/2022/06/27/21/35/00/pref-14-large.jpg", "data/pref-14-large.jpg")
if not wc.fetch_weathermap():
    print("failure fetch weather map")
