import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pydantic import ValidationError

import db
import kb
from env import *

basic_router = Router()
admin_id = []


async def send_pdf_file(message: types.Message):
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


EVENTS_PER_PAGE = 5
total_pages = (len(kb.urlkb.inline_keyboard) + EVENTS_PER_PAGE - 1) // EVENTS_PER_PAGE


def generate_events_pagination(current_page):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    # Добавляем кнопки с мероприятиями для текущей страницы
    start = (current_page - 1) * EVENTS_PER_PAGE
    end = start + EVENTS_PER_PAGE
    for button in kb.urlkb.inline_keyboard[start:end]:
        keyboard.inline_keyboard.append([*button])

    control = []
    # Добавляем кнопки для пагинации
    if current_page > 1:
        control.append(InlineKeyboardButton(text="◀️", callback_data=f"page_{current_page - 1}"))
    else:
        control.append(InlineKeyboardButton(text="◀️", callback_data="none", disabled=True))

    control.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="none", disabled=True))

    if current_page < total_pages:
        control.append(InlineKeyboardButton(text="▶️", callback_data=f"page_{current_page + 1}"))
    else:
        control.append(InlineKeyboardButton(text="▶️", callback_data="none", disabled=True))

    keyboard.inline_keyboard.append(control)

    return keyboard


# вызов, после нажатия старт, клавиатуры (кнопки - новый маршрут, библиотека карт) и программы ДОДа
@basic_router.message(Command('start'))
async def commands_start(message: types.Message):
    user_id = message.from_user.id
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO user_stat (user_id, timestamp) VALUES (?, ?)', (user_id, timestamp))
    conn.commit()
    await send_pdf_file(message)
    await message.answer('Чтобы продолжить, нажмите на кнопку «Новый маршрут», кнопка расположена внизу экрана.',
                         reply_markup=kb.startkb)


# обновление бота
@basic_router.message(Command('restart'))
async def commands_restart(message: types.Message):
    await send_pdf_file(message)
    await message.answer('Чтобы продолжить, нажми на кнопку «Новый маршрут», кнопка расположена внизу экрана.',
                         reply_markup=kb.startkb)


# команда для отправления ссылки на сайт библиотеки карт
@basic_router.message(F.text == 'Библиотека карт 🗺')
async def open_website(message: types.Message):
    user_id = message.from_user.id
    timestampurl = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO url (user_id, timestamp) VALUES (?, ?)', (user_id, timestampurl))
    conn.commit()

    website_url = 'https://mospolynavigation.github.io/dod/'
    await message.answer(f'Перейти к просмотру → <a href="{website_url}">«Библиотека карт»</a>',
                         disable_web_page_preview=True)


@basic_router.message(F.text == 'Программа ДОД 📄')
async def send_dod_program(message: types.Message):
    await send_pdf_file(message)
    user_id = message.from_user.id
    timestampurl = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO file_stats (user_id, timestamp) VALUES (?, ?)', (user_id, timestampurl))
    conn.commit()


# region Опрос

# получение результатов опроса
@basic_router.message(Command('results'))
async def results(message: types.Message):
    await message.answer(
        f"Результаты опроса: \n\"Отлично:\" {poll_results['0']}\n\"Хорошо:\" {poll_results['1']}\n\"Удовлетворительно:\" {poll_results['2']}\n\"Плохо:\" {poll_results['3']}\n\"Ужасно:\" {poll_results['4']}\n")


@basic_router.poll_answer()
async def poll_answer_handler(answer: types.PollAnswer):
    if answer.user.id not in voted_users:
        voted_users.append(answer.user.id)
        poll_results.update({f'{answer.option_ids[0]}': poll_results[f'{answer.option_ids[0]}'] + 1})
        with open('./poll.json', 'w') as f:
            json.dump(poll_results, f)
        await bot.send_message(answer.user.id, "Спасибо за оценку!")
    else:
        await bot.send_message(answer.user.id, "Вы уже дали свою оценку!")


@basic_router.message(Command('poll'))
async def poll_command(message: types.Message):
    if message.from_user.id in voted_users:
        await message.answer("Вы уже дали свою оценку!")
        return
    await message.answer_poll(question='День открытых дверей окончен.\nПожалуйста, оцените работу бота',
                              options=['Отлично',
                                       'Хорошо',
                                       'Удовлетворительно',
                                       'Плохо',
                                       'Ужасно'],
                              is_anonymous=False,
                              type='regular',
                              allows_multiple_answers=False)


# endregion


# команда для бота, чтобы статистику для кнопки старт, здесь выводим только данные по новым пользователям, без общего количества кликов
@basic_router.message(Command('users'))
async def get_users_stat(message: types.Message):
    # определяем начальное и конечное время из самых ранних и поздних записей в базе данных
    cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM user_stat')
    start_time_str, end_time_str = cursor.fetchone()
    start_time = datetime.fromisoformat(start_time_str)  # преобразуем полученные строки с датами в объекты datetime
    end_time = datetime.fromisoformat(end_time_str)

    total_users, total_clicks = await db.count_users_button('user_stat', start_time_str,
                                                            end_time_str)  # считаем общее количество пользвателей за указанный диапазон (от самой ранней записи в БД до самой поздней)

    current_month = start_time.replace(day=1)  # задаём начальный месяц
    response_text = f'<b><i>Новые пользователи:</i></b> {total_users}\n\n'

    months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь',
              'Декабрь']

    while current_month <= end_time:
        month_start = current_month
        month_name = months[current_month.month - 1]  # задаём название текущего месяца
        if current_month.month == 12:
            month_end = current_month.replace(year=current_month.year + 1, month=1, day=1) - timedelta(seconds=1)
        else:
            month_end = current_month.replace(month=current_month.month + 1) - timedelta(seconds=1)

        users_month, total_month = await db.count_users_month('user_stat', month_start,
                                                              month_end)  # считаем количество пользователей за текущий месяц
        response_text += f'за {month_name} {current_month.year}: {users_month}\n'

        current_month = month_end + timedelta(seconds=1)  # переходим к следующему месяцу

    await message.answer(response_text, parse_mode=ParseMode.HTML)


# команда для бота, чтобы увидеть статистику для кнопки "Библиотека карт" - (новые пользователи + все клилки на кнопку)
@basic_router.message(Command('url'))
async def get_users_url(message: types.Message):
    # определяем начальное и конечное время из самых ранних и поздних записей в базе данных
    cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM url')
    start_time_str, end_time_str = cursor.fetchone()
    start_time = datetime.fromisoformat(start_time_str)  # преобразуем полученные строки с датами в объекты datetime
    end_time = datetime.fromisoformat(end_time_str)

    total_url, total_entries = await db.count_users_button('url', start_time_str,
                                                           end_time_str)  # считаем общее количество пользвателей за указанный диапазон (от самой ранней записи в БД до самой поздней)

    current_month = start_time.replace(day=1)  # задаём начальный месяц
    response_text = f'<b><i>Новые пользователи:</i></b> {total_url}\n'
    response_text += f'-------------------------------------\n<b><i>Всего вхождений:</i></b> {total_entries}\n\n'

    months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь',
              'Декабрь']

    while current_month <= end_time:
        month_start = current_month
        month_name = months[current_month.month - 1]  # задаём название текущего месяца
        if current_month.month == 12:
            month_end = current_month.replace(year=current_month.year + 1, month=1, day=1) - timedelta(seconds=1)
        else:
            month_end = current_month.replace(month=current_month.month + 1) - timedelta(seconds=1)

        users_month_url, total_month_entries = await db.count_users_month('url', month_start,
                                                                          month_end)  # считаем количество пользователей за текущий месяц
        response_text += f'за {month_name} {current_month.year}:\nновые {users_month_url}\nвсего {total_month_entries}\n\n'

        current_month = month_end + timedelta(seconds=1)  # переходим к следующему месяцу

    await message.answer(response_text, parse_mode=ParseMode.HTML)


# команда для бота, чтобы увидеть статистику кнопки "Программа ДОД" - (новые пользователи + все клилки на кнопку)                                                                                                                                                       (для программы ДОД)
@basic_router.message(Command('file'))
async def get_file_stats(message: types.Message):
    cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM file_stats')
    start_time_str, end_time_str = cursor.fetchone()
    start_time = datetime.fromisoformat(start_time_str)  # преобразуем полученные строки с датами в объекты datetime
    end_time = datetime.fromisoformat(end_time_str)

    total_users, total_file = await db.count_users_button('file_stats', start_time_str, end_time_str)
    response_text = f'<b><i>Новые пользователи:</i></b> {total_users}\n'
    response_text += f'-------------------------------------\n<b><i>Всего вхождений:</i></b> {total_file}\n\n'

    current_month = start_time.replace(day=1)
    months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь',
              'Декабрь']

    while current_month <= end_time:
        month_start = current_month
        month_name = months[current_month.month - 1]
        if current_month.month == 12:
            month_end = current_month.replace(year=current_month.year + 1, month=1, day=1) - timedelta(seconds=1)
        else:
            month_end = current_month.replace(month=current_month.month + 1) - timedelta(seconds=1)

        users_month, total_month_file = await db.count_users_month('file_stats', month_start, month_end)
        response_text += f'за {month_name} {current_month.year}:\nновые {users_month}\nвсего {total_month_file}\n\n'

        current_month = month_end + timedelta(seconds=1)

    await message.answer(response_text, parse_mode=ParseMode.HTML)


# получение результатов опроса
@basic_router.message(Command('results'))
async def results(message: types.Message):
    user_id = message.from_user.id
    if user_id in poll_results:
        total = poll_results[user_id].options
        await message.answer(f'Результаты опроса:\n {total} ')
    else:
        await message.answer('Результаты опроса еще не доступны')


# эта штучка нужна, если вдруг пользователь нажмёт в описании бота на данную команду (по факту делает то же самое, что и команда старт)
@basic_router.message(Command('newroute'))
async def commands_start(message: types.Message):
    await message.answer("Чтобы продолжить, нажми на кнопку «Новый маршрут», она находится внизу экрана:",
                         reply_markup=kb.startkb)


# вывод сообщения после нажатия на кнопку новый маршрут
@basic_router.message(F.text == 'Новый маршрут 📌')
async def url_command(message: types.Message):
    current_page = 1
    keyboard = generate_events_pagination(current_page)
    await message.answer('Выбери, что хочешь посетить:  👀', reply_markup=keyboard)


@basic_router.callback_query(F.data.startswith("page_"))
async def handle_pagination(callback: types.CallbackQuery):
    current_page = int(callback.data.split("_")[1])
    keyboard = generate_events_pagination(current_page)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


# отправление инлайн-кнопок со ссылками на соцсети
@basic_router.message(F.text == 'Наши соцсети ✉')
async def url_command(message: types.Message):
    await message.answer(
        'Выберите соцсеть',
        reply_markup=kb.builder)


# отправление списка доступных команд, для админовых и простых смертных соответственно
@basic_router.message(Command('commands'))
async def send_commands(message: types.Message):
    if message.from_user.id in admin_id:
        commands_text = "Команды, которыми Вы можете воспользоваться:\n\n/users - количество новых пользователей\n\n/url - количество новых пользователей, перешедших по ссылке\n\n/file - количество пользователей, которые нажали на кнопку запроса файла программы ДОД\n\n/network - количество новых пользователей перешедших по кнопке на соцсети"
    else:
        commands_text = "Команды, которыми Вы можете воспользоваться:\n\n/description - Описание бота\n\n/restart - Обновление бота\n\n/newroute - Новый маршрут"

    await message.answer(commands_text)


# команда описания бота
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
    await bot.send_message(callback_query.from_user.id,
                           'Ты можешь поучаствовать сразу в нескольких викторинах:\nв холле корпуса А пройдут\n«Интеллектуальная викторина о научных открытиях на стенде СНО», «Викторина по английскому языку»\nа также в аудитории А112а\n«Викторина от центра проектной деятельности»')

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
    await bot.send_message(callback_query.from_user.id,
                           'Здесь ты сможешь узнать всё о поступлении, а также об изменениях в ЕГЭ по физике, русскому языку, математике, литературе.')

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
    await bot.send_message(callback_query.from_user.id,
                           'Паблик-толк с блогером в сфере автоспорта Игорем Асановым.\n\n🤔Задумывались о том, как превратить своё хобби в профессию?\n\nНа День открытых дверей мы пригласили документалиста и блогера в сфере автоспорта Игоря Асанова. На паблик-токе мы обсудим, как сочетать несочетаемое и выбрать профессию по интересам так, чтобы потом не разочароваться. Начинайте готовить свои вопросы!\n\nКонечно, познакомим вас с флагманскими проектами, покажем студенческие разработки на выставке проектной деятельности и расскажем про науку и внеучебную жизнь в университете.\n\nУвидимся в 11:00 в аудитории А200!')

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
    await bot.send_message(callback_query.from_user.id,
                           'Здесь помимо просмотра выставки проектов, вы также сможете поучаствовать в увлекательных викторинах и мастер-классах от центра проектной деятельности.')

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
    await bot.send_message(callback_query.from_user.id,
                           'Cтенды информации:\n«Инженерная школа»\n«Курсы подготовки к ЕГЭ»\n«Договорной отдел»\nнаходятся в аудитории - В104\n\nCтенды информации:\n«Профсоюзной организации работников и обучающихся»\n«Управления студенческого городка»\n«Управления по международной интеграции и работе с иностранными студентами»\nнаходятся в аудитории - В105')

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


@basic_router.callback_query(F.data == 'v2')
async def v2_call(callback: types.CallbackQuery):
    await callback.message.answer('Выбери мастер-класс по интересующему тебя направлению:', reply_markup=kb.inmkb)
    await callback.answer()


@basic_router.callback_query(F.data == 'm1')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id,
                           'Мастер-классы по направлению «Арт, дизайн и медиа» проходят в аудиториях Б303, Б306, Б309, Б310, Б410')

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
    await bot.send_message(callback_query.from_user.id,
                           'Мастер-классы по направлению «Урбанистика» от факультета урбанистики и городского хозяйства проходят в аудитории Б307')

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
    await bot.send_message(callback_query.from_user.id,
                           'Мастер-классы по направлению «Бизнес» от факультета экономики и управления проходят в аудитории Б311')

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
    await bot.send_message(callback_query.from_user.id,
                           'Мастер-классы по направлению «Информационные технологии» проходят в аудитории Н305')

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
    await bot.send_message(callback_query.from_user.id,
                           'Мастер-класс по направлению «Экология и технологии жизни» от Факультета химической технологии и биотехнологии пройдёт в аудитории Б303.')

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
    await bot.send_message(callback_query.from_user.id,
                           'Мастер-класс по направлению «Технологии, материалы и производство» от факультета химической технологии и биотехнологии, а также факультета машиностроения и полиграфического института пройдёт в аудитории Б303.')

    cursor.execute(
        "SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 10")  # 43 по логике, но маршрут повторяется с 10 строкой
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
    await bot.send_message(callback_query.from_user.id,
                           'Мастер-класс по направлению «Транспорт, цифра, логистика» от транспортного факультета пройдут в аудитории Б411')

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


@basic_router.callback_query(F.data == 'v1')
async def v2_call(callback: types.CallbackQuery):
    await callback.message.answer('Выбери, что хочешь посетить:', reply_markup=kb.inkb)
    await callback.answer()


# официальная часть
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
async def v2_call(callback: types.CallbackQuery):
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
async def v2_call(callback: types.CallbackQuery):
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
