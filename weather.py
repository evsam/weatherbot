from datetime import datetime
import sqlite3
import requests


def get_weather_text(forecast_data, city_name):
    weather_text = f"Погода на три дня в г. {city_name}.\n\n"
    if len(forecast_data) == 0:
        return None

    for day_weather in forecast_data:
        forecast_date = day_weather.get('forecastDate')
        date = datetime.strptime(forecast_date, '%Y-%m-%d')
        date_text = date.strftime('%d %B')
        min_temp = day_weather.get('minTemp')
        max_temp = day_weather.get('maxTemp')
        weather_description = day_weather.get('weather')
        date_line = f"{date_text}: от {min_temp} до {max_temp} ℃, {weather_description}"
        if weather_description.count('снег') > 0:
             date_line += '❄️\n'
        elif weather_description.count('ясно') > 0:
             date_line += '☀️\n'
        elif weather_description.count('дождь') > 0:
             date_line += '🌧\n'
        else:
            date_line += '\n'
        weather_text += date_line
    return weather_text

def parse_weather_response(data):
    city = data.get('city')
    time_zone = city.get('timeZone', '+0200')
    weather_text = get_weather_text(city['forecast']['forecastDay'], city.get('cityName'))
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
        return None

def get_city_ind(city):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute("SELECT city_id FROM cities WHERE city = '%s'" % city)
    city_index = cur.fetchone()
    cur.close()
    conn.close()

    if city_index is not None:
        return city_index[0]
    else:
        return None