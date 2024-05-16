import sqlite3
import json
import codecs

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
# подключение к базе данных
conn = sqlite3.connect('my.db')
cursor = conn.cursor()

# инстанс бота
TOKEN = '7063579287:AAESk8F9-4FpcpLfIRJHm4faCzFF_9eDESk'
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)


# проголосовавшие пользователи
voted_users = []

poll_results : dict = json.loads(open('poll.json').read())


# кнопки
inline_kbs = {}
with open('kb.json', 'r', encoding='utf-8-sig') as f: inline_kbs = json.load(f)