import asyncio
import logging
import calendar

from contextlib import suppress
from datetime import datetime, timedelta

from aiogram import types, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from pydantic import ValidationError

import db
import kb
import re
from env import *

basic_router = Router()
admin_id = [1708607317, 305487694]

#вызов, после нажатия старт, клавиатуры (кнопки - новый маршрут, библиотека карт) и программы ДОДа
@basic_router.message(Command('start'))
async def commands_start(message: types.Message):
    user_id = message.from_user.id
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO classic_users (user_id, timestamp) VALUES (?, ?)', (user_id, timestamp))
    conn.commit()

    await message.answer('Чтобы продолжить, нажмите на кнопку «Новый маршрут», кнопка расположена внизу экрана.', reply_markup=kb.startkb)


#обновление бота
@basic_router.message(Command('restart'))
async def commands_restart(message: types.Message):
    await message.answer('Чтобы продолжить, нажми на кнопку «Новый маршрут», кнопка расположена внизу экрана.', reply_markup=kb.startkb)

@basic_router.message(Command('url'))
async def commands_url(message: types.Message):
    await message.answer('Данная команда пока не доступна\n(╮°-°)╮┳━┳       (╯°□°)╯︵ ┻━┻ ')

@basic_router.message(Command('commands'))
async def send_commands(message: types.Message):
    if message.from_user.id in admin_id: 
        commands_text = "Команды, которыми Вы можете воспользовтаься:\n\n/users - Узнать количество новых пользователей\n\n/url - Узнать количество новых пользователей, перешедших по ссылке"
    else:
        commands_text = "Команды, которыми Вы можете воспользовтаься:\n\n/description - Описание бота\n\n/restart - Обновление бота\n\n/newroute - Новый маршрут"
    
    await message.answer(commands_text)

#команда для бота, чтобы увидеть общее количество новых пользователей за выбранный период времени
@basic_router.message(Command('users'))
async def get_users_stat(message: types.Message):
    #определяем начальное и конечное время из самых ранних и поздних записей в базе данных
    cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM classic_users')
    start_time_str, end_time_str = cursor.fetchone()
    start_time = datetime.fromisoformat(start_time_str)#преобразуем полученные строки с датами в объекты datetime 
    end_time = datetime.fromisoformat(end_time_str)

    total_users = await db.count_users_stat(start_time_str, end_time_str)#считаем общее количество пользвателей за указанный диапазон (от самой ранней записи в БД до самой поздней) 

    current_month = start_time.replace(day=1)#задаём начальный месяц
    response_text = f'Общее количество пользователей за весь период: {total_users}\n\n'

    months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

    while current_month <= end_time:
        month_start = current_month
        month_name = months[current_month.month - 1] #задаём название текущего месяца  
        if current_month.month == 12: 
            month_end = current_month.replace(year=current_month.year + 1, month=1, day=1) - timedelta(seconds=1)
        else:
            month_end = current_month.replace(month=current_month.month + 1) - timedelta(seconds=1)

        users_month = await db.count_users_month(month_start, month_end) #считаем количество пользователей за текущий месяц
        response_text += f'за {month_name} {current_month.year}: {users_month}\n'

        current_month = month_end + timedelta(seconds=1)  #переходим к следующему месяцу

    await message.answer(response_text, parse_mode=ParseMode.HTML)

@basic_router.message(Command('results'))
async def results(message: types.Message):
    user_id = message.from_user.id
    if user_id in poll_results:
        total = poll_results[user_id].options
        await message.answer(f'Результаты опроса:\n {total} ')
    else:
        await message.answer('Результаты опроса еще не доступны')

#эта штучка нужна, если вдруг пользователь нажмёт в описании бота на данную команду (по факту делает то же самое, что и команда старт)
@basic_router.message(Command('newroute'))
async def commands_start(message: types.Message):
    await message.answer("Чтобы продолжить, нажми на кнопку «Новый маршрут», она находится внизу экрана:", reply_markup=kb.startkb)

#вывод сообщения после нажатия на кнопку новый маршрут
@basic_router.message(F.text == 'Новый маршрут 📌')
async def url_command(message : types.Message):
	await message.answer('Что Вы хотите узнать?  👀', reply_markup=kb.urlkb)

@basic_router.message(F.text == 'Наши соцсети ✉')
async def url_command(message : types.Message):
    await message.answer(
        'Выберите соцсеть',
        reply_markup=kb.builder)

#команда описания бота
@basic_router.message(Command('description'))
async def cmd_description(message: types.Message):
    description_file = f'descriptions_language_ru.txt'
    try:
        with open(description_file, 'r', encoding='utf-8') as file:
            description = file.read()
            await message.answer(description, parse_mode="HTML")
            await message.answer('🕊')
    except FileNotFoundError:
        logging.error(f'Файл {description_file} не найден.')
        await message.answer('Описание не найдено.')

#вывод после выбора кнопки КАМПУСА
@basic_router.callback_query(F.data == 'campus')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Какой кампус Вам нужен?', reply_markup=kb.mapcampus)

#вывод после выбора кнопки ТОЧКА ИНТЕРЕСА
@basic_router.callback_query(F.data == 'pointinterest')
async def v2_call(callback : types.CallbackQuery):
	await callback.message.answer('По какому адресу Вы сейчас находитесь?', reply_markup=kb.map_pointinterest)
	await callback.answer()

#вывод после выбора кнопки АУДИТОРИИ
@basic_router.callback_query(F.data == 'auditorium')
async def first_function(callback : types.CallbackQuery):
  await callback.message.answer('❕Введите номер нужной аудитории в формате, который указан в Вашем расписании.\n\nНомер аудитории должен содержать буквенные символы, которые обозначают название кампуса, а также численные символы (4 цифры)\n\n❕<u>Пример ввода</u>:  Ав1407 \n"Ав"- обозначение кампуса на Автозаводской,\n"1" - корпус, "4" - этаж, "07" - аудитория.\n(На данный момент доступен первый корпус на ул.Автозаводская)', parse_mode="HTML")
  await callback.answer()

@basic_router.message()
async def second_function(message: types.Message):
    room = message.text.strip().upper() #приводим текст к верхнему регистру и убираем пробелы между символами

    query = "SELECT infa, fotka FROM Auditoriums WHERE room_number = ?"
    cursor.execute(query, (room,))
    row = cursor.fetchone()

    if re.match(r'^[а-яА-Я]{1,2}\d{3,4}[а-яА-Я]?$', room): #1-2 буквы и 3-4 цифры
        if row is not None:
            infa, fotka = row
            await message.reply(f"{infa}")
            await message.answer_photo(photo=fotka)
        else:
            await message.reply(f"Информация о маршруте до аудитории {room} не найдена.")
    '''else:
        await message.answer('Номер аудитории был введён некорректно.\nПовторите попытку.')'''


#Точки интереса на БС
@basic_router.callback_query(F.data == 'pointinterestBS')
async def w1_call(callback : types.CallbackQuery):
	await callback.message.answer('Вы выбрали кампус на Большой Семёновской\n"БС"-обозначение в Вашем расписании.')
	await callback.message.answer('Выберите, что Вы хотите посетить:', reply_markup=kb.map_BS)
	await callback.answer()


#Точки интереса на Ав
@basic_router.callback_query(F.data == 'pointinterestAv')
async def w1_call(callback : types.CallbackQuery):
	await callback.message.answer('Вы выбрали кампус на Автозаводской\n"Ав"-обозначение в Вашем расписании.')
	'''await callback.message.answer('Выберите, что Вы хотите посетить:', reply_markup=kb.map_BS)'''
	await callback.answer()

#Точки интереса на М
@basic_router.callback_query(F.data == 'pointinterestM')
async def w1_call(callback : types.CallbackQuery):
	await callback.message.answer('Вы выбрали кампус на Михалоковской\n"М"-обозначение в Вашем расписании.')
	'''await callback.message.answer('Выберите, что Вы хотите посетить:', reply_markup=kb.map_BS)'''
	await callback.answer()

#Точки интереса на Пр
@basic_router.callback_query(F.data == 'pointinterestPr')
async def w1_call(callback : types.CallbackQuery):
	await callback.message.answer('Вы выбрали кампус на Прянишкова\n"Пр"-обозначение в Вашем расписании.')
	'''await callback.message.answer('Выберите, что Вы хотите посетить:', reply_markup=kb.map_BS)'''
	await callback.answer()

#Точки интереса на ПК
@basic_router.callback_query(F.data == 'pointinterestPK')
async def w1_call(callback : types.CallbackQuery):
	await callback.message.answer('Вы выбрали кампус на Павла Корчагина\n"ПК"-обозначение в Вашем расписании.')
	'''await callback.message.answer('Выберите, что Вы хотите посетить:', reply_markup=kb.map_BS)'''
	await callback.answer()



