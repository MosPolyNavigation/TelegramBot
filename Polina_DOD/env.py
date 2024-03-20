import sqlite3

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
# подключение к базе данных
conn = sqlite3.connect('my.db')
cursor = conn.cursor()

# инстанс бота
TOKEN = ''
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)


# проголосовавшие пользователи
voted_users = []

poll_results = {
    0 : 0,          # Отлично
    1 : 0,          # Хорошо
    2 : 0,          # Удовлетворительно
    3 : 0,          # Плохо
    4 : 0,          # Ужасно
}
