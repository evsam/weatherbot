from dotenv import load_dotenv
import os


load_dotenv()

BOT_TIMEZONE = 5
TOKEN = os.getenv('TOKEN')
SQLITE_FILE = os.getenv('SQLITE_FILE')
WEATHER_SERVICE_URL = ('https://api.openweathermap.org/data/2.5/forecast?'
                       'q={city_name}&appid=aeebc2f45da9163d5a9a3c198b9cd7a6&units=metric&lang=ru')

