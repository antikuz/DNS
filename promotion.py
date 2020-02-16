
import requests
from bs4 import BeautifulSoup
import time
import re
from DNSsql import SQLdb


def promotion_page():
    url = r'https://www.dns-shop.ru/actions/'
    headers = {
        "Host": "www.dns-shop.ru",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.dns-shop.ru/",
        "Cookie": "city_path=norilsk",
    }
    r = requests.get(url, headers=headers, allow_redirects=True)
    # with open('resp.txt', 'w', encoding='utf-8') as fh:
    #     fh.write(r.text)
    return r.text

def parse_promo_products(url):
    headers = {
    "Host": "www.dns-shop.ru",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.dns-shop.ru/actions/",
    "Cookie": "city_path=norilsk",
    }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    products = []
    for product in soup.find_all('div', class_='n-catalog-product__main'):
        products.append(product.find('a', class_='ui-link').text)
    db = SQLdb()
    try:
        return db.promo_get_columns(products)
        """
        {'Колонки 2.0 Edifier R2700': (165280, 15599), 'Колонки 2.0 Edifier R980T': (177657, 3899)}
        """
    finally:
        db.close_db()

def convert_promo_dates(text):
    text = text.split()
    year = time.strftime("%y")
    monthes = {
        'января': '01',
        'февраля': '02',
        'марта': '03',
        'апреля': '04',
        'мая': '05',
        'июня': '06',
        'июля': '07',
        'августа': '08',
        'сентября': '09',
        'октября': '10',
        'ноября': '11',
        'декабря': '12'
    }
    if len(text) == 7 :
        start = f'{year}.{monthes[text[4]]}.{text[1]}'
        end =  f'{year}.{monthes[text[4]]}.{text[3]}'
    else:
        start = f'{year}.{monthes[text[2]]}.{text[1]}'
        end =  f'{year}.{monthes[text[5]]}.{text[4]}'
    return start, end

def main():
        soup = BeautifulSoup(promotion_page(), 'html.parser')
        promotions = soup.find('div', class_='actions-page__actions')
        for promotion in promotions.find_all('div', class_='action-card actions-page__action'):
            name = promotion.find('a', class_='action-card__title ui-link').text
            description = promotion.find('p', class_='action-card__desc').text
            dates = promotion.find('p', class_='action-card__dates').text
            try:
                link = promotion.find('a', class_='action-card__product-link ui-link ui-link_blue')['href']
                link = 'https://www.dns-shop.ru' + link
            except TypeError:
                continue

            percent = re.search(r'или (\d+)%', description)
            if percent:
                percent = int(percent[1])
            else:
                continue

            products = parse_promo_products(link)
            products_id = []
            products_update = []
            for product in products.keys():
                product_id = products[product][0]
                products_id.append(str(product_id))
                price = products[product][1]
                bonus = price * (percent / 100)
                products_update.append((product_id, bonus))
            
            products_id = ','.join(products_id)
            start_date, expires_date = convert_promo_dates(dates)
            print(name)
            db = SQLdb()
            try:
                db.insert_promo((name, description, start_date, expires_date, products_id))
                db.update_promo(products_update)
            finally:
                db.close_db()

main()