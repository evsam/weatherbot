from dotenv import load_dotenv
import os


load_dotenv()

BOT_TIMEZONE = 5
BOT_TOKEN = os.getenv('TOKEN')
SQLITE_FILE = os.getenv('SQLITE_FILE')
WEATHER_SERVICE_URL = os.getenv('WEATHER_SERVICE_URL')


