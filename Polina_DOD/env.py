from datetime import datetime
import sqlite3
import json
import os

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode


def adapt_datetime(ts):
    return ts.isoformat(" ")


def convert_datetime(ts):
    return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")


sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("timestamp", convert_datetime)

# подключение к базе данных
conn = sqlite3.connect('my.db')
cursor = conn.cursor()

# инстанс бота
# parse token from env if it exists or use default token
TOKEN = os.getenv('TOKEN')
if not TOKEN:
    TOKEN = ''

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)

# проголосовавшие пользователи
voted_users = []

poll_results: dict = json.loads(open('./poll.json').read())
