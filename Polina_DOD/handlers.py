import asyncio
import logging

from contextlib import suppress
from datetime import datetime

from aiogram import types, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from pydantic import ValidationError

import db
import kb
from env import *

basic_router = Router()

#вызов, после нажатия старт, клавиатуры (кнопки - новый маршрут, библиотека карт) и программы ДОДа
@basic_router.message(Command('start'))
async def commands_start(message: types.Message):
    user_id = message.from_user.id
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO user_stat (user_id, timestamp) VALUES (?, ?)', (user_id, timestamp))
    conn.commit()
    pdf_file = 'Программа Дня открытых дверей.pdf'

    try:
        file = types.FSInputFile(pdf_file)
        await bot.send_document(chat_id=message.chat.id, document=file)
    except FileNotFoundError:
        logging.error(f'Файл {pdf_file} не найден.')
        await message.answer('Файл не найден.')
    except ValidationError:
        logging.error(f'Ошибка валидации')
        await message.answer('Ошибка валидации.')
    await message.answer('Чтобы продолжить, нажмите на кнопку «Новый маршрут», кнопка расположена внизу экрана.', reply_markup=kb.startkb)

#обновление бота
@basic_router.message(Command('restart'))
async def commands_restart(message: types.Message):
    await message.answer('Чтобы продолжить, нажми на кнопку «Новый маршрут», кнопка расположена внизу экрана.', reply_markup=kb.startkb)

#команда для отправления ссылки на сайт библиотеки карт
@basic_router.message(F.text == 'Библиотека карт 🗺')
async def open_website(message: types.Message):
    user_id = message.from_user.id
    timestampurl = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO url (user_id, timestampurl) VALUES (?, ?)', (user_id, timestampurl))
    conn.commit()

    website_url = 'https://mospolynavigation.github.io/dod/'
    await message.answer(f'Перейти к просмотру → <a href="{website_url}">«Библиотека карт»</a>', disable_web_page_preview=True)

#команда для бота, чтобы увидеть общее количество новых пользователей за выбранный период времени
@basic_router.message(Command('users'))
async def get_users_stat(message: types.Message):
    start_time = '2023-01-01 00:00:00'  #начальное время
    end_time = '2024-12-31 23:59:59'  #конечное время
    total_users = await db.count_users_stat(start_time, end_time)

    end_December = '2023-12-31 23:59:59'
    start_December = '2023-12-01 00:00:00'
    users_December = await db.count_users_December(start_December, end_December)

    end_January = '2024-01-31 23:59:59'
    start_January = '2024-01-01 00:00:00'
    users_January = await db.count_users_January(start_January, end_January)

    end_February = '2024-02-29 23:59:59'
    start_February = '2024-02-01 00:00:00'
    users_February = await db.count_users_February(start_February, end_February)
    await message.answer(f'Общее количество пользователей за весь период времени: {total_users} \n\nза декабрь 2023: {users_December} \nза январь 2024: {users_January} \nза февраль 2024: {users_February}')

#команда для бота, чтобы увидеть общее количество пользователей за выбранный период времени (для библиотеки карт)
@basic_router.message(Command('url'))
async def get_users_url(message: types.Message):
    start_url = '2023-01-01 00:00:00'  #начальное время
    end_url = '2024-12-31 23:59:59'  #конечное время
    total_url = await db.count_users_url(start_url, end_url)

    end_url_December = '2023-12-31 23:59:59'
    start_url_December = '2023-12-01 00:00:00'
    users_url_December = await db.count_users_url_December(start_url_December, end_url_December)

    end_url_January = '2024-01-31 23:59:59'
    start_url_January = '2024-01-01 00:00:00'
    users_url_January = await db.count_users_url_January(start_url_January, end_url_January)

    end_url_February = '2024-02-29 23:59:59'
    start_url_February = '2024-02-01 00:00:00'
    users_url_February = await db.count_users_url_February(start_url_February, end_url_February)
    await message.answer(f'Общее количество пользователей за весь период времени, перешедших по ссылке: {total_url} \n\nза декабрь 2023: {users_url_December}  \nза январь 2024: {users_url_January} \nза февраль 2024: {users_url_February} ')

#получение результатов опроса
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
	await message.answer('Выбери, что хочешь посетить:  👀', reply_markup=kb.urlkb)

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

@basic_router.callback_query(F.data == 'v3')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Узнать всё о поступлении, ты сможешь в холле корпуса А')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 3")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'v14')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 41")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'v12')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 12")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'v13')
async def handle_tok1(callback_query: types.CallbackQuery):


    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 13")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

'''@basic_router.callback_query(F.data == 'v10')
async def handle_tok1(callback_query: types.CallbackQuery):
    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 10")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)'''

@basic_router.callback_query(F.data == 'v11')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Ты можешь поучаствовать сразу в нескольких викторинах:\nв холле корпуса А пройдут\n«Интеллектуальная викторина о научных открытиях на стенде СНО», «Викторина по английскому языку»\nа также в аудитории А112а\n«Викторина от центра проектной деятельности»')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 111")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'v8')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Здесь ты сможешь узнать всё о поступлении, а также об изменениях в ЕГЭ по физике, русскому языку, математике, литературе.')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 3")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'v7')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Паблик-толк с блогером в сфере автоспорта Игорем Асановым.\n\n🤔Задумывались о том, как превратить своё хобби в профессию?\n\nНа День открытых дверей мы пригласили документалиста и блогера в сфере автоспорта Игоря Асанова. На паблик-токе мы обсудим, как сочетать несочетаемое и выбрать профессию по интересам так, чтобы потом не разочароваться. Начинайте готовить свои вопросы!\n\nКонечно, познакомим вас с флагманскими проектами, покажем студенческие разработки на выставке проектной деятельности и расскажем про науку и внеучебную жизнь в университете.\n\nУвидимся в 11:00 в аудитории А200!')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 7")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, map)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'v4')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Здесь помимо просмотра выставки проектов, вы также сможете поучаствовать в увлекательных викторинах и мастер-классах от центра проектной деятельности.')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 4")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)


@basic_router.callback_query(F.data == 'v5')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Посетить «Выставочные зоны» можно в аудиториях Б303 и Б410')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 5")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'v6')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 6")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'v9')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Cтенды информации:\n«Инженерная школа»\n«Курсы подготовки к ЕГЭ»\n«Договорной отдел»\nнаходятся в аудитории - В104\n\nCтенды информации:\n«Профсоюзной организации работников и обучающихся»\n«Управления студенческого городка»\n«Управления по международной интеграции и работе с иностранными студентами»\nнаходятся в аудитории - В105')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 9")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data=='v2')
async def v2_call(callback : types.CallbackQuery):
	await callback.message.answer('Выбери мастер-класс по интересующему тебя направлению:', reply_markup=kb.inmkb)
	await callback.answer()

@basic_router.callback_query(F.data == 'm1')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Мастер-классы по направлению «Арт, дизайн и медиа» проходят в аудиториях Б303, Б306, Б309, Б310, Б410')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 21")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'm2')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Мастер-классы по направлению «Урбанистика» от факультета урбанистики и городского хозяйства проходят в аудитории Б307')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 22")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)


@basic_router.callback_query(F.data == 'm4')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Мастер-классы по направлению «Бизнес» от факультета экономики и управления проходят в аудитории Б311')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 24")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'm5')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Мастер-классы по направлению «Информационные технологии» проходят в аудитории Н305')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 25")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'm3')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Мастер-класс по направлению «Экология и технологии жизни» от Факультета химической технологии и биотехнологии пройдёт в аудитории Б303.')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 23")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'm7')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Мастер-класс по направлению «Технологии, материалы и производство» от факультета химической технологии и биотехнологии, а также факультета машиностроения и полиграфического института пройдёт в аудитории Б303.')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 10") #43 по логике, но маршрут повторяется с 10 строкой
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'm6')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Мастер-класс по направлению «Транспорт, цифра, логистика» от транспортного факультета пройдут в аудитории Б411')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 26")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data=='v1')
async def v2_call(callback : types.CallbackQuery):
	await callback.message.answer('Выбери, что хочешь посетить:', reply_markup=kb.inkb)
	await callback.answer()

#официальная часть
@basic_router.callback_query(F.data == 'w1')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 11")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

'''@basic_router.callback_query(F.data == 'w4')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Трансляция официальной части будет проходить в аудиториях: Б303 и Б404')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 14")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)'''


@basic_router.callback_query(F.data == 'w2')
async def v2_call(callback : types.CallbackQuery):
	await callback.message.answer('Выбери с деканом какого факультета ты хочешь встретиться:', reply_markup=kb.inwkb)
	await callback.answer()


@basic_router.callback_query(F.data == 'ww1')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 121")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'ww2')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 122")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'ww3')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 123")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'ww4')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 124")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'ww5')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 125")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'ww6')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 126")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)


@basic_router.callback_query(F.text == 'w3')
async def v2_call(callback : types.CallbackQuery):
	await callback.message.answer('Выбери с директором какого института ты хочешь встретиться:', reply_markup=kb.ynwkb)
	await callback.answer()



@basic_router.callback_query(F.data == 'yw1')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 131")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'yw2')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 132")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@basic_router.callback_query(F.data == 'yw3')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 133")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        fcam = types.BufferedInputFile(fcam, "fcam")
        fotka = types.BufferedInputFile(fotka, "fotka")
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)