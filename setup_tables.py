import codecs
import sqlite3
from import_cities import import_cities

def create_users_table():
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, user_chat_id int NOT NULL, city_id varchar(25) NOT NULL, time_zone varchar(10) NOT NULL, bot_message_time varchar(20), user_message_time varchar(20))')
    conn.commit()
    cur.close()
    conn.close()


def main_setup():
    import_cities()
    create_users_table()

