import sqlite3
import json
import os

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

poll_results:dict = json.loads(open('Polina_DOD\\poll.json').read())
