from utils import is_time, to_timezone_for_bot
import sqlite3
from datetime import datetime


def select_bot_message_time(connect, message):
    connect = sqlite3.connect('db.sqlite')
    cur = connect.cursor()
    cur.execute("SELECT bot_message_time FROM users WHERE user_chat_id = '%s'" % message.chat.id)
    user_data = cur.fetchone()
    cur.close()
    return user_data

def select_user_message_time(connect, message):
    cur = connect.cursor()
    is_user_message_time = (
        cur.execute("SELECT user_message_time FROM users WHERE user_chat_id = '%s'" % message.chat.id)).fetchone()
    cur.close()
    return is_user_message_time

def select_user_view_information(connect, message):
    cur = connect.cursor()
    cur.execute('SELECT cities.city, users.user_message_time\
             FROM users INNER JOIN cities\
             ON users.city_id = cities.city_id AND user_chat_id = "%s"' % message.chat.id)
    info = cur.fetchone()
    cur.close()
    return info

def update_is_running_to_continue(connect, message):
    cur = connect.cursor()
    cur.execute("UPDATE users SET is_running = 1 WHERE user_chat_id = '%s'" % message.chat.id)
    connect.commit()
    cur.close()

def select_is_running(connect, message):
    cur = connect.cursor()
    is_running = (cur.execute("SELECT is_running FROM users WHERE user_chat_id = '%s'" % message.chat.id)).fetchone()
    cur.close()
    return is_running

def update_is_running_to_stop(connect, message):
    cur = connect.cursor()
    cur.execute("UPDATE users SET is_running = 0 WHERE user_chat_id = '%s'" % message.chat.id)
    connect.commit()
    cur.close()

def reset_user_data(connect, message):
    cur = connect.cursor()
    cur.execute("DELETE FROM users WHERE user_chat_id = %s" % message.chat.id)
    connect.commit()
    cur.close()
    bot.send_message(message.chat.id, 'Бот перезапущен. Назовите город, в котором вы проживаете:')

def select_user_data(connect, message):
    cur = connect.cursor()
    cur.execute("SELECT time_zone, user_message_time FROM users WHERE user_chat_id = '%s'" % message.chat.id)
    user_data = cur.fetchone()
    cur.close()
    return user_data

def register_user(connect, message, city_index, time_zone):
    user_chat_id = message.chat.id
    cur = connect.cursor()
    cur.execute("INSERT INTO users (user_chat_id, city_id, time_zone) VALUES ('%s', '%s', '%s')" % (
    user_chat_id, city_index, time_zone))
    connect.commit()
    cur.close()

def register_time(connect, message, time_zone):
    user_message_time = message.text
    bot_message_time = to_timezone_for_bot(message.text, BOT_TIMEZONE, time_zone)
    cur = connect.cursor()
    cur.execute("UPDATE users SET bot_message_time = '%s', user_message_time = '%s', is_running = 1 WHERE user_chat_id = '%s'" % (bot_message_time, user_message_time, message.chat.id))
    connect.commit()
    cur.close()

def select_users_info_with_same_time(connect):
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    cur = connect.cursor()
    cur.execute(
        'SELECT user_chat_id, city_id FROM users WHERE bot_message_time = "%s" and is_running = 1' % current_time)
    user_records = cur.fetchall()
    cur.close()
    return user_records