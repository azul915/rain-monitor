import urllib.error
import urllib.request

def fetch_wethermap(url, dst_path):
    try:
        with urllib.request.urlopen(url) as web_file:
            weather_map = web_file.read()
            with open(dst_path, mode='wb') as local_file:
                local_file.write(weather_map)
    except urllib.error.URLError as e:
        print(e)

fetch_wethermap("https://static.tenki.jp/static-images/radar/2022/06/27/21/35/00/pref-14-large.jpg", "data/pref-14-large.jpg")