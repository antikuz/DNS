import os
import sqlite3


class SQLdb():
    def __init__(self):
        dbfile = f'{os.path.dirname(os.path.realpath(__file__))}\\DNSdb.sqlite'
        if os.path.exists(dbfile):
            self.db = sqlite3.connect(dbfile)
            self.db.execute("PRAGMA foreign_keys = ON")
            self.cursor = self.db.cursor()
        else:
            self.db = sqlite3.connect(dbfile)
            self.db.execute("PRAGMA foreign_keys = ON")
            self.cursor = self.db.cursor()
            self.cursor.execute('''CREATE TABLE products(
                id INTEGER PRIMARY KEY, 
                name TEXT, 
                available TEXT, 
                price INTEGER, 
                bonus INTEGER, 
                bonus_promo INTEGER, 
                update_date TEXT
                )'''
            )
            self.cursor.execute('''CREATE TABLE price_history(
                id_product INTEGER,
                price INTEGER,
                up_date TEXT,
                FOREIGN KEY(id_product) REFERENCES products(id) ON DELETE CASCADE
                )'''
            )
            self.cursor.execute('''CREATE TABLE promo(
                id TEXT,
                name TEXT,
                description TEXT,
                start_date TEXT,
                expires_date TEXT,
                products TEXT
                )'''
            )
            self.db.commit()
        self.inscount = 0
        self.insbonus = 0
        self.histcount = 0
        self.promocount = 0

    def close_db(self):
        self.db.close()
        text = []
        if self.inscount:
            text.append(f'We have inserted {self.inscount} product records')
        if self.histcount:
            text.append(f'We have inserted {self.histcount} price history records')
        if self.insbonus:
            text.append(f'We have inserted {self.insbonus} promo records')
        if self.promocount:
            text.append(f'We have updated {self.promocount} promo bonus records')
        print('\n'.join(text))

    def insert_products(self, product_list, price_history):
        products = []
        for product_id in product_list:
            name = product_list[product_id]['name']
            available = product_list[product_id]['available']
            price = product_list[product_id]['price']
            bonus = product_list[product_id]['bonus']
            bonus_promo = product_list[product_id]['bonus_promo']
            update_time = product_list[product_id]['update_time']
            products.append((product_id, name, available, price, bonus, bonus_promo, update_time))

        self.cursor.executemany('INSERT OR REPLACE INTO products VALUES(?,?,?,?,?,?,?)', products)
        self.inscount += self.cursor.rowcount

        price_history = [(x, price_history[x]['price'], price_history[x]['update_time']) for x in price_history]
        self.cursor.executemany('INSERT OR REPLACE INTO price_history VALUES(?,?,?)', price_history)
        self.histcount += self.cursor.rowcount
        self.db.commit()
    
    def price_comparison(self, id_list):
        self.cursor.execute(f'SELECT id, price, bonus FROM products WHERE id in ({",".join(["?"]*len(id_list))})', id_list)
        objects = self.cursor.fetchall()
        objects = {x[0]: {'price': x[1], 'bonus': x[2]} for x in objects}
        return objects

    def promo_get_products(self, promo_product):
        self.cursor.execute(f'SELECT id, name, price FROM products WHERE name in ({",".join(["?"]*len(promo_product))})', promo_product)
        objects = self.cursor.fetchall()
        objects = {x[0]: {'name': x[1], 'price': x[2]} for x in objects}
        return objects

    def insert_promo(self, promo):
        self.cursor.execute('INSERT OR REPLACE INTO promo VALUES(?,?,?,?,?,?)', promo)
        self.insbonus += self.cursor.rowcount
        self.db.commit()
    
    def update_promo(self, products):
        for product in products:
            self.cursor.execute(f'UPDATE products SET bonus_promo = {int(product[1])} WHERE id = "{product[0]}"')
            self.promocount += self.cursor.rowcount
        self.db.commit()
    
    def get_products_with_bonuses(self):
        self.cursor.execute(f'SELECT name, price, bonus, bonus_promo from products WHERE bonus > 0 OR bonus_promo > 0')
        return self.cursor.fetchall()
    
    def get_promotions(self):
        self.cursor.execute(f'SELECT id from promo')
        promotions = self.cursor.fetchall()
        promotions = [x[0] for x in promotions]
        return promotions

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            print(exc_type)
        if exc_value:
            print(exc_value)

        self.close_db()
        return True