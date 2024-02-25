import sqlite3

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode

#подключение к базе данных
conn = sqlite3.connect('my.db')
cursor = conn.cursor()

#инстанс бота
TOKEN = '6959853578:AAG7DlllIQ5GynnPZrdfHgbKiqp1vyaixrE'
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)

#переменная для хранения результатов опросов
poll_results = {}  
