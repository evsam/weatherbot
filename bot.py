import telebot
from telebot import types
from weather import get_city_ind
from weather import get_weather
from setup_tables import main_setup
from dotenv import load_dotenv
import os
import schedule
import time
import threading
from sql_functions import *

BOT_TIMEZONE = 5

main_setup()

load_dotenv()
TOKEN = os.getenv('TOKEN')
sqlite_file = os.getenv('SQLITE_FILE')

bot = telebot.TeleBot(TOKEN)

print('Bot started')

@bot.message_handler(commands=['reset'])
def reset(message):
    conn = sqlite3.connect(sqlite_file)
    reset_user_data(conn, message)
    conn.close()

@bot.message_handler(commands=['stop'])
def stop(message):
    conn = sqlite3.connect(sqlite_file)
    is_running = select_is_running(conn, message)
    if is_running[0] is None:
        bot.send_message(message.chat.id, 'Вы еще не ввели все нужные данные, чтобы бот остановил свою работу.')
        return
    if is_running[0] == 0:
        bot.send_message(message.chat.id, 'Ваш бот уже остановлен.')
        return
    update_is_running_to_stop(conn, message)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Возобновить работу бота.", callback_data="continue"))
    bot.send_message(message.chat.id, 'Бот остановил свою работу. Чтобы возобновить его работу, нажмите /continue', reply_markup=markup)
    conn.close()

@bot.message_handler(commands=['continue'])
def continue_work(message):
    conn = sqlite3.connect(sqlite_file)
    is_running = select_is_running(conn, message)
    if is_running[0] is None:
        bot.send_message(message.chat.id, 'Вы еще не ввели все нужные данные, чтобы бот продолжил свою работу.')
        return
    if is_running[0] == 1:
        bot.send_message(message.chat.id, 'Ваш бот уже запущен.')
        return
    update_is_running_to_continue(conn, message)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Остановить работу бота.", callback_data="stop"))
    bot.send_message(message.chat.id, 'Бот возобновил свою работу. Чтобы остановить его работу, нажмите /stop', reply_markup=markup)
    conn.close()

@bot.message_handler(commands=['view'])
def view(message):
    conn = sqlite3.connect(sqlite_file)
    is_user_message_time = select_user_message_time(conn, message)
    if is_user_message_time[0] is None:
        bot.send_message(message.chat.id, 'Вы еще не ввели все нужные данные, чтобы посмотреть их.')
        return
    info = select_user_view_information(conn, message)
    info_city = info[0].capitalize()
    info_time = info[1]
    info_text = f'<b>Город:</b> {info_city}\n<b>Время отправки:</b> {info_time}'
    bot.send_message(message.chat.id, info_text, parse_mode='html')
    conn.close()

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect(sqlite_file)
    user_data = select_bot_message_time(conn, message)
    if user_data is None:
        bot.send_message(message.chat.id, 'Здравствуйте. Назовите город, в котором вы проживаете:')
    else:
        bot.send_message(message.chat.id,
                         'Извините, вы уже начали работу этого бота. Чтобы его <b>перезапустить</b>, используйте /reset', parse_mode='html')
    conn.close()

@bot.message_handler(content_types=['text'])
def send_id(message):
    conn = sqlite3.connect(sqlite_file)
    user_data = select_user_data(conn, message)
    if user_data is None:
        enter_city(conn, message)
        return
    time_zone = user_data[0]
    message_time = user_data[1]
    if message_time is None:
        enter_time(conn, message, time_zone)
    else:
        default_message(message)

    conn.close()

@bot.callback_query_handler(func=lambda call: call.data == 'view')
def view_button_click(call):
    view(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'reset')
def reset_button_click(call):
    reset(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def stop_button_click(call):
    stop(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'continue')
def continue_work_button_click(call):
    continue_work(call.message)



def enter_city(connect, message):
    city_index = get_city_ind(connect, str.lower(message.text))
    if city_index is None:
        bot.send_message(message.chat.id,'Извините, такого города нет😢. Введите название административного центра вашей области.')
        return
    weather = get_weather(city_index)
    if weather is None:
        bot.send_message(message.chat.id, 'Извините, что-то пошло не так(. Введите город еще раз.')
        return
    if weather[1] is None:
        bot.send_message(message.chat.id, 'Погода по этому городу, к сожалению, не доступна. Введите другой город.')
        return
    register_user(connect, message, city_index, weather[0])
    bot.send_message(message.chat.id, f'<b>{weather[1]}</b>', parse_mode='html')
    bot.send_message(message.chat.id,'Теперь укажите <b>время</b>, во сколько мне присылать этот прогноз:\n<i>(Пример: 6:00, 15:35)</i>',parse_mode='html')

def enter_time(connect, message, time_zone):
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
        register_time(connect, message, time_zone)
        bot.send_message(message.chat.id,
                         f'Отлично!🤙🏼 Я вас запомнил, теперь буду присылать прогноз погоды каждый день в <b>{message.text}</b>!🕔\n\nТакже вы можете воспользоваться /stop, чтобы <b>остановить</b> работу бота, и /continue, чтобы <b>возобновить</b> работу бота',
                         reply_markup=markup, parse_mode='html')

def default_message(message):
    bot.send_message(message.chat.id, 'Для остановки отправки прогнозов введите /stop')

def send_weather_message(city_id, user_chat_id_list):
    weather = get_weather(city_id)
    for user_chat_id in user_chat_id_list:
        bot.send_message(user_chat_id, f'<b>{weather[1]}</b>', parse_mode='html')

def run_continuously(interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

def check_users_time():
    connect = sqlite3.connect('db.sqlite')
    user_records = select_users_info_with_same_time(connect)
    cities = []
    for user_city in user_records:
        user_chat_id = user_city[0]
        city_id = user_city[1]
        found = [cities_item for cities_item in cities if cities_item["city_id"] == city_id]
        if len(found) > 0:
            existing_city_users = found[0]
            existing_city_users["users"].append(user_chat_id)
        else:
            city_users = {'city_id': city_id, 'users': [user_chat_id]}
            cities.append(city_users)
    for city_data in cities:
        send_weather_message(city_data['city_id'], city_data['users'])
    connect.close()

schedule.every(1).minutes.at(':00').do(check_users_time)
run_continuously()

bot.infinity_polling()
