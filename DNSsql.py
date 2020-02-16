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
                name TEXT,
                description TEXT,
                start_date TEXT,
                expires_date TEXT,
                products TEXT
                )'''
            )
            self.db.commit()
        self.inscount = 0
        self.chcount = 0

    def close_db(self):
        self.db.close()
        print(f'''We have inserted {self.inscount} records to the table products
We have inserted {self.chcount} records to the table price_history''')
    
    def insert_products(self, product_list, price_history):
        self.cursor.executemany('INSERT OR REPLACE INTO products VALUES(?,?,?,?,?,?,?)', product_list)
        self.inscount += self.cursor.rowcount
        price_history = [(x[0], x[3], x[6]) for x in price_history]
        self.cursor.executemany('INSERT OR REPLACE INTO price_history VALUES(?,?,?)', price_history)
        self.chcount += self.cursor.rowcount
        self.db.commit()
    
    def price_comparison(self, id_list):
        self.cursor.execute(f'SELECT id, price, bonus FROM products WHERE id in ({",".join(["?"]*len(id_list))})', id_list)
        objects = self.cursor.fetchall()
        return {x[0]: (x[1],x[2]) for x in objects}

    def promo_get_columns(self, promo_product):
        self.cursor.execute(f'SELECT id, name, price FROM products WHERE name in ({",".join(["?"]*len(promo_product))})', promo_product)
        objects = self.cursor.fetchall()
        return {x[1]: (x[0],x[2]) for x in objects}

    def insert_promo(self, promo):
        self.cursor.execute('INSERT OR REPLACE INTO promo VALUES(?,?,?,?,?)', promo)
        self.inscount += self.cursor.rowcount
        self.db.commit()
    
    def update_promo(self, products):
        for product in products:
            self.cursor.execute(f'UPDATE products SET bonus_promo = {int(product[1])} WHERE id = "{product[0]}"')
            self.chcount += self.cursor.rowcount
        self.db.commit()
    
    def get_products_with_bonuses(self):
        self.cursor.execute(f'SELECT name, price, bonus, bonus_promo from products WHERE bonus > 0 OR bonus_promo > 0')
        return self.cursor.fetchall()