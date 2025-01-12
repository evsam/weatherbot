from dotenv import load_dotenv
import os


load_dotenv()

BOT_TIMEZONE = 5
TOKEN = os.getenv('TOKEN')
SQLITE_FILE = os.getenv('SQLITE_FILE')


