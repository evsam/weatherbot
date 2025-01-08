from utils import is_time, to_timezone_for_bot
import telebot
from telebot import types
from weather import get_city_ind
from weather import get_weather
from setup_tables import main_setup
import sqlite3
from dotenv import load_dotenv
import os
from datetime import datetime
import schedule
import time
import traceback

BOT_TIMEZONE = 5

main_setup()

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

print('Bot started')

def check_users_time():
    now = datetime.now()
    # current_time = now.strftime('%H:%M')
    current_time = '12:00'
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute('SELECT user_chat_id, city_id FROM users WHERE bot_message_time = "%s"' % current_time)
    user_records = cur.fetchall()
    cities = []
    for user_city in user_records:
        user_chat_id = user_city[0]
        city_id = user_city[1]
        print("city_id", city_id)
        # found = list(filter(lambda cities_item: cities_item["city_id"] == city_id, cities))
        found = [cities_item for cities_item in cities if cities_item["city_id"] == city_id]
        print(found)
        if len(found) > 0:
            existing_city_users = found[0]
            existing_city_users["users"].append(user_chat_id)

        else:
            city_users = {'city_id': city_id, 'users': [user_chat_id]}
            cities.append(city_users)
            print(cities)


# schedule.every(1).minutes.at(':00').do(check_users_time)

# @bot.message_handler(commands=['stop'])
# def stop(message):
#     bot.send_message(message.chat.id, 'Бот остановлен. Чтобы возобновить его работу, нажмите /continue')





def reset_user_data(message):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_chat_id = %s" % message.chat.id)
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Бот перезапущен. Назовите город, в котором вы проживаете:')

@bot.message_handler(commands=['reset'])
def reset(message):
    reset_user_data(message)


@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute("SELECT message_time FROM users WHERE user_chat_id = '%s'" % message.chat.id)
    user_data = cur.fetchone()
    cur.close()
    conn.close()

    if user_data is None:
        bot.send_message(message.chat.id, 'Здравствуйте. Назовите город, в котором вы проживаете:')
    else:
        bot.send_message(message.chat.id,
                         'Извините, вы уже начали работу этого бота. Чтобы его <b>перезапустить</b>, используйте /reset', parse_mode='html')


@bot.message_handler(content_types='text')
def send_id(message):
    print(message.text)
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute("SELECT time_zone, user_message_time FROM users WHERE user_chat_id = '%s'" % message.chat.id)
    user_data = cur.fetchone()
    cur.close()
    conn.close()

    if user_data is None:
        enter_city(message)
        return
    time_zone = user_data[0]
    message_time = user_data[1]
    if message_time is None:
        enter_time(message, time_zone)
    else:
        default_message(message)

# @bot.message_handler(func=lambda message: True)
# def default(message):
#     bot.send_message(message.chat.id, 'введите текст')

def enter_city(message):
    city_index = get_city_ind(str.lower(message.text))
    if city_index is not None:
        weather = get_weather(city_index)
        if weather is not None:
            if weather[1] is not None:
                register_user(message, city_index, weather[0])
                bot.send_message(message.chat.id, f'<b>{weather[1]}</b>', parse_mode='html')
                bot.send_message(message.chat.id,
                             'Теперь укажите <b>время</b>, во сколько мне присылать этот прогноз:\n<i>(Пример: 6:00, 15:35)</i>',
                             parse_mode='html')
            else:
                bot.send_message(message.chat.id, 'Погода по этому городу, к сожалению, не доступна. Введите другой город.')
        else:
            bot.send_message(message.chat.id, 'Извините, что-то пошло не так(. Введите город еще раз.')
    else:
        bot.send_message(message.chat.id,
                         'Извините, такого города нет😢. Введите название административного центра вашей области.')


def enter_time(message, time_zone):
    markup = types.InlineKeyboardMarkup()
    btn_view = types.InlineKeyboardButton('Посмотреть данные👀', callback_data='view')
    btn_reset = types.InlineKeyboardButton('Перезапустить бота↪️', callback_data='reset')
    btn_stop = types.InlineKeyboardButton('Остановить бота❌', callback_data='stop')
    markup.row(btn_view)
    markup.row(btn_reset, btn_stop)
    message_time = message.text
    if not is_time(message_time):
        bot.send_message(message.chat.id, 'Извините😢, время было введено неправильно, попробуйте еще раз.')
    else:
        register_time(message, time_zone)
        bot.send_message(message.chat.id,
                         f'Отлично!🤙🏼 Я вас запомнил, теперь буду присылать прогноз погоды каждый день в <b>{message.text}</b>!🕔\n\nТакже вы можете воспользоваться /stop, чтобы <b>остановить</b> работу бота, и /continue, чтобы <b>возобновить</b> работу бота',
                         reply_markup=markup, parse_mode='html')


def default_message(message):
    try:
        check_users_time()
    except Exception:
        traceback.print_exc()

    bot.send_message(message.chat.id, 'Для остановки отправки прогнозов введите /stop')



def register_user(message, city_index, time_zone):
    user_chat_id = message.chat.id
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (user_chat_id, city_id, time_zone) VALUES ('%s', '%s', '%s')" % (
    user_chat_id, city_index, time_zone))
    conn.commit()
    cur.close()
    conn.close()

def register_time(message, time_zone):
    user_message_time = message.text
    bot_message_time = to_timezone_for_bot(message.text, BOT_TIMEZONE, time_zone)
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute("UPDATE users SET bot_message_time = '%s', user_message_time = '%s'" % (bot_message_time, user_message_time))
    conn.commit()
    cur.close()
    conn.close()

@bot.callback_query_handler(func=lambda call: call.data == 'view')
def view(call):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute('SELECT cities.city, users.user_message_time\
     FROM users INNER JOIN cities\
     ON users.city_id = cities.city_id AND user_chat_id = "%s"' % call.message.chat.id)
    info = cur.fetchone()
    info_city = info[0].capitalize()
    info_time = info[1]
    info_text = f'<b>Город:</b> {info_city}\n<b>Время отправки:</b> {info_time}'
    bot.send_message(call.message.chat.id, info_text, parse_mode='html')

@bot.callback_query_handler(func=lambda call: call.data == 'reset')
def view(call):
    reset_user_data(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def view(call):
    bot.send_message(call.message.chat.id, "stop")

def send_weather_message(city_id, user_chat_id_list):
    weather = get_weather(city_id)
    for user_chat_id in user_chat_id_list:
        bot.send_message(user_chat_id, f'<b>{weather[1]}</b>', parse_mode='html')

bot.infinity_polling()

# while True:
#     schedule.run_pending()
#     time.sleep(1)


