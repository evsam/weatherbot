import codecs
import sqlite3


def create_table():
    conn = sqlite3.connect('data_base/db.sqlite')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS cities (id INTEGER PRIMARY KEY AUTOINCREMENT, country varchar(50) NOT NULL, city varchar(50) NOT NULL, city_id varchar(25) NOT NULL)')
    conn.commit()
    cur.close()
    conn.close()


def main():
    create_table()

    with codecs.open('full_city_list.txt', encoding='utf-8') as f:
        conn = sqlite3.connect('db.sqlite')
        for line in f:
            line_parts = line.split(';')
            country = line_parts[0].replace('"', '')
            city = line_parts[1].replace('"', '')
            city_id = line_parts[2].replace('"', '')
            cur = conn.cursor()
            cur.execute("INSERT INTO cities (country, city, city_id) VALUES ('%s', '%s', '%s')" % (country, city, city_id))
            conn.commit()
            cur.close()

            print(line.replace('\n', ''))

        conn.close()

if __name__ == "__main__":
    main()
