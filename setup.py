import sqlite3
import locale
import sys
from constants import SQLITE_FILE


def create_users_table(conn):
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users '
                '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'user_chat_id int NOT NULL, '
                'city_name varchar(100) NOT NULL, '
                'time_zone varchar(10) NOT NULL, '
                'bot_message_time varchar(20), '
                'user_message_time varchar(20), '
                'is_running bool)')
    conn.commit()
    cur.close()


def main_setup():
    if sys.platform == 'win32':
        locale.setlocale(locale.LC_ALL, 'rus_rus')
    else:
        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

    conn = sqlite3.connect(SQLITE_FILE)
    create_users_table(conn)
    conn.close()
