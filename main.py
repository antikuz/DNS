import requests
import os, time, shutil
from zipfile import ZipFile
import sqlite3
import xlrd
from DNSsql import SQLdb

HOME = os.path.dirname(os.path.realpath(__file__))

def get_file():
    url = r'https://www.dns-shop.ru/files/price/price-norilsk.zip'
    headers = {
        "Host": "www.dns-shop.ru",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.dns-shop.ru/order/begin/",
        "Connection": "keep-alive",
        "Cookie": "city_path=norilsk",
        "Cache-Control": "max-age=0",
        "TE": "Trailers",
    }
    r = requests.head(url, headers=headers)
    datefile = r.headers['Last-Modified']
    time_last_file = os.stat(f'{HOME}\\price-norilsk.zip').st_mtime
    timeformat = '%a, %d %b %Y %H:%M:%S %Z'
    time_new_file = time.mktime(time.strptime(datefile, timeformat))
    if time_new_file > time_last_file:
        time_file = time.strftime('%d.%m.%y', time.localtime(time_last_file))
        shutil.move(f'{HOME}\\price-norilsk.zip', f'{HOME}\\archive\\price-norilsk {time_file}.zip')
        r = requests.get(url, headers=headers)

        with open(f'{HOME}\\price-norilsk.zip', 'wb') as zipfh:
            zipfh.write(r.content)
        with ZipFile(f'{HOME}\\price-norilsk.zip', 'r') as zipObj:
            zipObj.extractall()

        os.utime(f'{HOME}\\price-norilsk.zip', (time_new_file, time_new_file))
        return True
    else:
        print('Nothing changes')
        return False

def parse_xls_sheet(db, sheet, update_time):
    products = dict()
    price_history = dict()
    for row in range(sheet.nrows):
        product_id = sheet.cell(row, 0).value

        try:
            product_id = int(product_id)
        except ValueError:
            continue

        product_name = sheet.cell(row, 1).value
        available_in_stores = ''
        for _ in range(2,6):
            available_in_stores += sheet.cell(row, _).value

        product_price = int(sheet.cell(row, 6).value)
        product_bonuses = int(sheet.cell(row, 7).value)
        product_promo_bonuses = 0
        products[product_id] = {
            'name': product_name, 
            'available': available_in_stores, 
            'price': product_price, 
            'bonus': product_bonuses,
            'bonus_promo': product_promo_bonuses, 
            'update_time': update_time
        }

        if len(products) == 100:
            old_products = db.price_comparison([product_id for product_id in products])
            for product_id in list(products):
                try:
                    new_price = products[product_id]['price']
                    new_bonus = products[product_id]['bonus']
                    old_price = old_products[product_id]['price']
                    old_bonus = old_products[product_id]['bonus']

                    if new_price != old_price or new_bonus != old_bonus:
                        if new_price != old_price:
                            price_history[product_id] = products[product_id]
                        continue
                    else:
                        del products[product_id]
                except KeyError:
                    continue

            db.insert_products(products, price_history)
            products = dict()
            price_history = dict()
    
    if len(products) > 0:
        db.insert_products(products, price_history)
        

def parse_xls_book():
    with xlrd.open_workbook(filename = f'{HOME}\\price-norilsk.xls', logfile=open(os.devnull, 'w')) as wb:
        db = SQLdb()
        try:
            sheet_numbers = wb.nsheets
            sheet_range = range(1, sheet_numbers - 1)
            update_time = time.strftime('%y.%m.%d', time.localtime(os.stat('price-norilsk.zip').st_mtime))
            for active_sheet in sheet_range:
                sheet = wb.sheet_by_index(active_sheet)
                parse_xls_sheet(db, sheet, update_time)
        finally:
            db.close_db()

def best_offers():
    with SQLdb() as db:
        best_price = []
        products = db.get_products_with_bonuses()
        for product in products:
            bonus = product[2] + product[3]
            discount_percent = bonus // (product[1] / 100)
            if discount_percent > 24:
                best_price.append((product[0], product[1], bonus,discount_percent))
        with open('temp\\result.csv', 'w') as fh:
            fh.write('sep=;\n')
            for product in (sorted(best_price, key = lambda x: x[3]))[::-1]:
                fh.write('{};{};{};{};\n'.format(*product))

def main():
    if get_file():
        print('Get new database from dns-shop, parse data')
        parse_xls_book()
    else:
        """
        wait for next check, probably 1 hour
        """
        pass

parse_xls_book()