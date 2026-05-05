import json
from AIanalyst import AIanalyst
import sqlite3

class DataLoading:
    def __init__(self):
        self.data_source=AIanalyst()

    def create_db(self):
        with sqlite3.connect('result_by_AI.db') as connection:
            cursor = connection.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS results_analyse(    
                                percent_scam INTEGER NOT NULL,
                                verdict TEXT NOT NULL)
                           ''')
            connection.commit()

    def load_data(self):
        clean_data = self.data_source.text_analysis().strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed=json.loads(clean_data)
        listing=parsed['listings']

        with sqlite3.connect('result_by_AI.db') as connection:
            cursor = connection.cursor()

            for i in listing:
                percent_scam=i['scam_probability']
                verdict=i['verdict']

            cursor.execute('''
                INSERT INTO results_analyse
                (percent_scam, verdict)
                VALUES (?, ?)
            ''', (percent_scam, verdict))
            connection.commit()

db = DataLoading()
db.create_db()
db.load_data()