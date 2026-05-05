import sqlite3
from scraping import *

class DataBase:
    def __init__(self):
        self.scrap_data = Scraper()


    def create_table(self):
        with sqlite3.connect('pages.db') as connection:
            cursor = connection.cursor()
            cursor.execute('''
                 CREATE TABLE IF NOT EXISTS pages (
                     id INTEGER PRIMARY KEY
                     , price DECIMAL(10,3) NOT NULL
                     , description VARCHAR(2000) NOT NULL
                     , publication_data DATETIME NOT NULL
                     , ai_risk_score DECIMAL(10,2)
                     , red_flags VARCHAR(500) 
                     , green_flags VARCHAR(500)
                 )
            ''')
            connection.commit()

    def get_data(self):
        with sqlite3.connect('pages.db') as connection:
            cursor = connection.cursor()

            for url in self.scrap_data.get_realty_data():
                try:
                    realty_id = url.get('realty_id')
                    price = url.get('price')
                    description = url.get('description_uk', '')
                    pub_date = url.get('publishing_date')
                    if not all([realty_id, price, pub_date]):
                        continue
                    cursor.execute(...)
                except Exception as e:
                    continue

                cursor.execute('''
                    INSERT OR IGNORE INTO pages (id, price, description, publication_data) 
                    VALUES (?, ?, ?, ?)
                ''', (realty_id, price, description, pub_date))

            connection.commit()

db = DataBase()
db.create_table()
db.get_data()