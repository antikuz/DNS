import requests
from bs4 import BeautifulSoup
import time
import re
from DNSsql import SQLdb
import logging

def promotion_page():
    url = r'https://www.dns-shop.ru/actions/#'
    headers = {
        "Host": "www.dns-shop.ru",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.dns-shop.ru/",
        "Cookie": "city_path=norilsk",
    }
    r = requests.get(url, headers=headers, allow_redirects=True)
    return r.text


def parse_promo_products(url):
    """
    Search names in db and return dict
    {
        165280: {
            'name': 'Колонки 2.0 Edifier R2700', 
            'price': 15599
        }, 
        177657: {
            'name': 'Колонки 2.0 Edifier R980T',
            'price': 3899
        }
    }
    """

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
        name = product.find('a', class_='ui-link').text
        print(f'    {name}')
        products.append(name)
    with SQLdb() as db:
        return db.promo_get_products(products)


def convert_promo_dates(text):
    """
    Convert 'с 7 по 29 февраля 2020 года' to '20.02.07', '20.02.29'
    Convert 'с 10 февраля по 15 марта 2020 года' to '20.02.10', '20.03.15'
    Convert 'с 10 февраля 2019 по 15 марта 2020 года' to '19.02.10', '20.03.15'
    """

    text = text.split()
    year = time.strftime("%y")
    months = {
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
        start = f'{year}.{months[text[4]]}.{text[1].zfill(2)}'
        end =  f'{year}.{months[text[4]]}.{text[3].zfill(2)}'
    elif len(text) == 8:
        start = f'{year}.{months[text[2]]}.{text[1].zfill(2)}'
        end =  f'{year}.{months[text[5]]}.{text[4].zfill(2)}'
    else:
        start = f'{text[3][-2:]}.{months[text[2]]}.{text[1].zfill(2)}'
        end = f'{text[-2][-2:]}.{months[text[-3]]}.{text[-4].zfill(2)}'

    return start, end


def main():
    with SQLdb() as db:
        db.clean_promo()
        db_promotions = db.get_promotions()
    soup = BeautifulSoup(promotion_page(), 'html.parser')
    promotions = soup.find('div', class_='actions-page__actions')
    for promotion in promotions.find_all('div', class_='action-card actions-page__action'):
        name = promotion.find('a', class_='action-card__title ui-link').text
        id_promo = promotion.find('a', class_='action-card__title ui-link')['href'].split('/')[-2]
        if id_promo in db_promotions:
            print('Уже в базе:', name)
            continue
        if 'Рассрочка' not in name:
            continue
        else:
            print(name)
        description = promotion.find('p', class_='action-card__desc').text
        dates = promotion.find('p', class_='action-card__dates').text
        try:
            link = promotion.find('a', class_='action-card__product-link ui-link ui-link_blue')['href']
            link = 'https://www.dns-shop.ru' + link
        except TypeError:
            continue

        percent = re.search(r'или .*(\d+)%', description)
        if percent:
            percent = int(percent[1])
        else:
            continue

        products = parse_promo_products(link)
        products_update = []
        for product_id in products:
            price = products[product_id]['price']
            bonus = price * (percent / 100)
            products_update.append((product_id, bonus))
        
        products_id = ','.join([str(x) for x in products])
        start_date, expires_date = convert_promo_dates(dates)

        with SQLdb() as db:
            db.insert_promo((id_promo, name, description, start_date, expires_date, products_id))
            db.update_promo(products_update)