from dotenv import load_dotenv
import os


load_dotenv()

BOT_TIMEZONE = 5
TOKEN = os.getenv('TOKEN')
SQLITE_FILE = os.getenv('SQLITE_FILE')
WEATHER_SERVICE_URL = 'https://worldweather.wmo.int/ru/json/{city_id}_ru.xml'

