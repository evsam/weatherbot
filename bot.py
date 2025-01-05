import telebot
import sqlite3
from telebot import types
import requests
from datetime import datetime

# Погода на три дня.
# 6 января: от -7 до -5 С
# 7 января: от -10 до -9 С
# 8 января: от -10 до -1 С

def get_weather_text(forecast_data):
    weather_text = "Погода на три дня.\n"
    for day_weather in forecast_data:
        forecast_date = day_weather.get('forecastDate')
        date = datetime.strptime(forecast_date, '%Y-%m-%d')
        date_text = date.strftime('%d %B')
        min_temp = day_weather.get('minTemp')
        max_temp = day_weather.get('maxTemp')
        date_line = f"{date_text}: от {min_temp} до {max_temp} C\n"
        weather_text += date_line
    return weather_text

def parse_weather_response(data):
    city = data.get('city')
    time_zone = city.get('timeZone', '+0200')
    weather_text = get_weather_text(city['forecast']['forecastDay'])
    return [time_zone, weather_text]

def get_weather(city_id):
    url = f'https://worldweather.wmo.int/ru/json/{city_id}_ru.xml'
    response = requests.get(url)
    if not response.ok:
        return None

    try:
        json_data = response.json()
        return parse_weather_response(json_data)
    except ValueError:
        return None  # Обрабатываем ситуацию некорректного JSON.

# bot = telebot.TeleBot('7704185699:AAG-Ub0Lc24mbMXcN31err790tlIJ3dlPmA')
#
# @bot.message_handler(commands=['start'])
# def start(message):
#     bot.send_message(message.chat.id, 'start')
#
#
# bot.polling(non_stop=True)

print(get_weather('659')[1])