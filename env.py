import sqlite3
import json
import codecs

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
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

poll_results:dict = json.loads(open('./poll.json').read())
