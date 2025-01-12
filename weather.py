from datetime import datetime, timedelta
import requests
import dotenv
from dotenv import load_dotenv
import os

load_dotenv()
WEATHER_SERVICE_URL = os.getenv('WEATHER_SERVICE_URL')

def get_day_part(date):
    if 6 <= date.hour <= 11:
        return 'Утро'
    if 12 <= date.hour <= 17:
        return 'День'
    if 18 <= date.hour <= 23:
        return 'Вечер'
    return 'Ночь'

def get_weather_text(forecast_list, city_name):
    weather_text = f"Прогноз погоды в г. {city_name}.\n\n"
    days_count = 0
    date_text_prev = None
    days_count_prev = 0
    if len(forecast_list) == 0:
        return None
    for forecast_day in forecast_list:
        forecast_date = forecast_day['dt_txt']
        date = datetime.strptime(forecast_date, '%Y-%m-%d %H:%M:%S')
        offset = timedelta(hours=5)
        if date.hour == 9 or date.hour == 15 or date.hour == 21 or date.hour == 3:
            city_date = date + offset
            day_time_text = get_day_part(city_date)
            date_text = city_date.strftime('%d %b')
            if date_text != date_text_prev:
                date_text_prev = date_text
                days_count+=1
                if days_count != days_count_prev and days_count != 1:
                    days_count_prev = days_count
                    weather_text += '\n'
                if days_count == 4:
                    break
                weather_text += f'<i>{date_text}</i>:\n'
            weather_text += f'     <b>{day_time_text}</b>'

        else:
            continue
        weather_description = forecast_day['weather'][0]['description']
        current_temp = forecast_day['main']['temp']
        weather_text += f', {str(int(current_temp))}°C, {weather_description}'
        if weather_description.count('ясно') > 0:
            weather_text += ' ☀\n'
        elif weather_description.count('снег') > 0:
            weather_text += ' ❄\n'
        elif weather_description.count('пасм') > 0:
            weather_text += ' ☁\n'
        elif weather_description.count('обл') > 0:
            weather_text += ' ⛅\n'
        else:
            weather_text += '\n'


    return weather_text

def parse_weather_response(data):
    city_name = data['city']['name']
    time_zone = data['city']['timezone']
    weather_text = get_weather_text(data['list'], city_name)
    return [time_zone, weather_text]


def get_weather(city_name):
    url = WEATHER_SERVICE_URL.replace('{city_name}', city_name)
    response = requests.get(url)
    if not response.ok:
        if response.status_code == 404:
            return [None,None]
        return None
    try:
        json_data = response.json()
        return parse_weather_response(json_data)
    except ValueError:
        return None



