import requests
import os, logging, time, shutil
from zipfile import ZipFile
import sqlite3
import xlrd
from DNSsql import SQLdb
import promotion

HOME = os.path.dirname(os.path.realpath(__file__))

proxies = {
 'http': 'http://51.77.235.246:4446',
 'https': 'http://51.77.235.246:4446',
}
def get_file():
    url = r'https://www.dns-shop.ru/files/price/price-spb.zip'
    headers = {
        "Host": "www.dns-shop.ru",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.dns-shop.ru/order/begin/",
        "Connection": "keep-alive",
        "Cookie": "city_path=spb",
        "Cache-Control": "max-age=0",
        "TE": "Trailers",
    }
    r = requests.head(url, headers=headers)
    datefile = r.headers['Last-Modified']
    time_last_file = os.stat(f'{HOME}\\price-spb.zip').st_mtime
    timeformat = '%a, %d %b %Y %H:%M:%S %Z'
    time_new_file = time.mktime(time.strptime(datefile, timeformat))
    if time_new_file > time_last_file:
        time_file = time.strftime('%y.%m.%d', time.localtime(time_last_file))
        if os.path.exists(f'{HOME}\\archive_spb\\price-spb {time_file}.zip'):
            shutil.move(f'{HOME}\\price-spb.zip', f'{HOME}\\archive_spb\\price-spb {time_file}_2.zip')
        else:
            shutil.move(f'{HOME}\\price-spb.zip', f'{HOME}\\archive_spb\\price-spb {time_file}.zip')
        
        r = requests.get(url, headers=headers, proxies=proxies)
        with open(f'{HOME}\\price-spb.zip', 'wb') as zipfh:
            zipfh.write(r.content)
        with ZipFile(f'{HOME}\\price-spb.zip', 'r') as zipObj:
            zipObj.extractall()

        os.utime(f'{HOME}\\price-spb.zip', (time_new_file, time_new_file))
        return True
    else:
        return False

if __name__ == "__main__":
    get_file()