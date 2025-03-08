import telebot
from telebot import types
from weather import  get_weather
from utils import is_time
from setup import main_setup
import schedule
import sqlite3
import time
import threading
from sql_functions import *
from constants import BOT_TOKEN, SQLITE_FILE
import logging

main_setup()
bot = telebot.TeleBot(BOT_TOKEN)

logging.basicConfig(filename='/var/www/python/weatherbot/debug.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)


logging.info('Bot started')

@bot.message_handler(commands=['reset'])
def reset(message):
    conn = sqlite3.connect(SQLITE_FILE)
    reset_user_data(conn, message)
    bot.send_message(message.chat.id, 'Я перезапущен. Назовите город, в котором вы проживаете:')
    conn.close()


@bot.message_handler(commands=['stop'])
def stop(message):
    conn = sqlite3.connect(SQLITE_FILE)
    is_running = select_is_running(conn, message)
    if is_running is None or is_running[0] is None:
        bot.send_message(message.chat.id, 'Вы еще не ввели все нужные данные, чтобы я остановил свою работу.')
        return
    if is_running[0] == 0:
        bot.send_message(message.chat.id, 'Я уже остановлен.')
        return
    update_is_running_to_stop(conn, message)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Возобновить работу бота.↪️", callback_data="continue"))
    bot.send_message(message.chat.id,
                     'Я остановил свою работу. Чтобы ее <b>возобновить</b>, нажмите /continue.\n\n'
                     'После этого я снова начну присылать вам ежедневно прогноз погоды в <b>указанное время</b>.',
                     reply_markup=markup, parse_mode='html')
    conn.close()


@bot.message_handler(commands=['continue'])
def continue_work(message):
    conn = sqlite3.connect(SQLITE_FILE)
    is_running = select_is_running(conn, message)
    if is_running is None or is_running[0] is None:
        bot.send_message(message.chat.id, 'Вы еще не ввели все нужные данные, чтобы я продолжил свою работу.')
        return
    if is_running[0] == 1:
        bot.send_message(message.chat.id, 'Я уже запущен.')
        return
    update_is_running_to_continue(conn, message)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Остановить работу бота.❌", callback_data="stop"))
    info = select_user_view_information(conn, message)
    info_city = info[0].capitalize()
    info_time = info[1]
    info_text = f'<b>Город:</b> {info_city}\n<b>Время отправки:</b> {info_time}'
    bot.send_message(message.chat.id,
                     f'Я возобновил свою работу. Напомню ваши <b>настройки отправки</b>. '
                     f'Их вы также можете всегда посмотреть с помощью команды /view.😉'
                     f'\n\n{info_text}\n\nЧтобы <b>остановить</b> мою работу, нажмите /stop.',
                     reply_markup=markup, parse_mode='html')
    conn.close()


@bot.message_handler(commands=['view'])
def view(message):
    conn = sqlite3.connect(SQLITE_FILE)
    is_user_message_time = select_user_message_time(conn, message)
    if is_user_message_time is None or is_user_message_time[0] is None:
        bot.send_message(message.chat.id, 'Вы еще не ввели все нужные данные, чтобы посмотреть их.😢')
        return
    info = select_user_view_information(conn, message)
    info_city = info[0].capitalize()
    info_time = info[1]
    info_text = (f'Вот ваши данные отправки!\n\n<b>Город:</b> {info_city}\n<b>Время отправки:</b> {info_time}\n\n'
                 f'В любой момент вы можете перезапустить меня командой /reset, и изменить свои данные на другие.')
    bot.send_message(message.chat.id, info_text, parse_mode='html')
    conn.close()


@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect(SQLITE_FILE)
    user_data = select_bot_message_time(conn, message)
    if user_data is None:
        bot.send_message(message.chat.id, 'Здравствуйте🖐🏽. Я бот, который будет <b>отслеживать прогноз погоды</b> '
                                          'и <b>ежедневно</b> присылать его вам в указанное время. '
                                          'Назовите город, в котором вы проживаете:', parse_mode='html')
    else:
        bot.send_message(message.chat.id,
                         'Извините, вы уже начали мою работу.😢\n\n'
                         'Чтобы меня <b>перезапустить</b>, используйте /reset. Все ваши данные удалятся и вам придется вводить новые.',
                         parse_mode='html')
    conn.close()


@bot.message_handler(content_types=['text'])
def text_message(message):
    conn = sqlite3.connect(SQLITE_FILE)
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
    city_name = str.lower(message.text)
    weather = get_weather(city_name)
    if weather is None:
        bot.send_message(message.chat.id, 'Извините, что-то пошло не так😢. Введите город еще раз.')
        return
    if weather[1] is None:
        bot.send_message(message.chat.id,
                         'Извините, такого города нет😢. Введите название административного центра.')
        return
    register_user(connect, message, city_name, weather[0])
    bot.send_message(message.chat.id, f'{weather[1]}', parse_mode='html')
    bot.send_message(message.chat.id,
                     'Теперь укажите <b>время</b>, во сколько мне присылать этот прогноз:\n'
                     '<i>(Пример: 6:00, 15:35)</i>',parse_mode='html')


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
                         f'Отлично!🤙🏼 Я вас запомнил, теперь буду присылать прогноз погоды каждый день в '
                         f'<b>{message.text}</b>!🕔\n\nТакже вы можете воспользоваться /stop, '
                         f'чтобы <b>остановить</b> мою работу, и /continue, чтобы ее <b>возобновить</b>',
                         reply_markup=markup, parse_mode='html')


def default_message(message):
    bot.send_message(message.chat.id, 'Для остановки отправки прогнозов введите /stop')


def send_weather_message(city_name, user_chat_id_list):
    weather = get_weather(city_name)
    if weather is None or weather[1] is None:
        logging.error(f'error getting data for city: ${city_name}')
        return
    for user_chat_id in user_chat_id_list:
        logging.debug(f'send_message to:, {user_chat_id} of city: {city_name}')
        try:
            bot.send_message(user_chat_id, f'{weather[1]}', parse_mode='html')
        except Exception as e:
            logging.debug('message error: ', e)


def run_scheduler(interval=1):
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
        city_name = user_city[1]
        found = [cities_item for cities_item in cities if cities_item["city_name"] == city_name]
        if len(found) > 0:
            existing_city_users = found[0]
            existing_city_users["users"].append(user_chat_id)
        else:
            city_users = {'city_name': city_name, 'users': [user_chat_id]}
            cities.append(city_users)
    for city_data in cities:
        send_weather_message(city_data['city_name'], city_data['users'])
    connect.close()


schedule.every(1).minutes.at(':00').do(check_users_time)
run_scheduler()



bot.infinity_polling()
