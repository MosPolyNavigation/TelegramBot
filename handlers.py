import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import types, F, Router
from aiogram.filters import Command, StateFilter
from pydantic import ValidationError

import db
from kb import *
from env import *
from fsm import *

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


# вызов, после нажатия старт, клавиатуры (кнопки - новый маршрут, библиотека карт) и программы ДОДа
@basic_router.message(Command('start'))
async def commands_start(message: types.Message):
    user_id = message.from_user.id
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO user_stat (user_id, timestamp) VALUES (?, ?)', (user_id, timestamp))
    conn.commit()
    await send_pdf_file(message)
    await message.answer('Чтобы продолжить, нажмите на кнопку «Новый маршрут», кнопка расположена внизу экрана.',
                         reply_markup=startkb)


# обновление бота
@basic_router.message(Command('restart'))
async def commands_restart(message: types.Message):
    await send_pdf_file(message)
    await message.answer('Чтобы продолжить, нажми на кнопку «Новый маршрут», кнопка расположена внизу экрана.',
                         reply_markup=startkb)


# команда для отправления ссылки на сайт библиотеки карт
@basic_router.message(F.text == 'Библиотека карт 🗺')
async def open_website(message: types.Message):
    user_id = message.from_user.id
    timestampurl = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO url (user_id, timestampurl) VALUES (?, ?)', (user_id, timestampurl))
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

#region Опрос
    
# получение результатов опроса
@basic_router.message(Command('results'))
async def results(message: types.Message):
    await message.answer(f"Результаты опроса: \n\"Отлично:\" {poll_results['0']}\n\"Хорошо:\" {poll_results['1']}\n\"Удовлетворительно:\" {poll_results['2']}\n\"Плохо:\" {poll_results['3']}\n\"Ужасно:\" {poll_results['4']}\n")

@basic_router.poll_answer()
async def poll_answer_handler(answer: types.PollAnswer):
    if answer.user.id not in voted_users:
        voted_users.append(answer.user.id)
        poll_results.update({f'{answer.option_ids[0]}' : poll_results[f'{answer.option_ids[0]}'] + 1})
        with open('Polina_DOD\\poll.json', 'w') as f:
            json.dump(poll_results, f)
        await bot.send_message(answer.user.id, "Спасибо за оценку!")
    else:
        await bot.send_message(answer.user.id, "Вы уже дали свою оценку!")

@basic_router.message(Command('poll'))
async def poll_command(message: types.Message):
    if message.from_user.id in voted_users:
        await message.answer("Вы уже дали свою оценку!")
        return
    await message.answer_poll(question = 'День открытых дверей окончен.\nПожалуйста, оцените работу бота', 
                              options = ['Отлично',
                                         'Хорошо',
                                         'Удовлетворительно', 
                                         'Плохо',
                                         'Ужасно'],
                              is_anonymous = False,
                              type = 'regular',
                              allows_multiple_answers = False)

#endregion


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

        users_month, total_month = await db.count_users_month('user_stat',month_start,
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
    response_text +=f'-------------------------------------\n<b><i>Всего вхождений:</i></b> {total_entries}\n\n' 

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
    response_text +=f'-------------------------------------\n<b><i>Всего вхождений:</i></b> {total_file}\n\n'

    current_month = start_time.replace(day=1)
    months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

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
                         reply_markup=startkb)


# вывод сообщения после нажатия на кнопку новый маршрут
@basic_router.message(F.text == 'Новый маршрут 📌')
async def url_command(message: types.Message):
    inline_kbs = load_data()
    events_kb.inline_keyboard = []
    for i in inline_kbs['events']:
        events_kb.inline_keyboard.append([InlineKeyboardButton(text=i['header'], callback_data=f"generic_{i['key']}")])
    await message.answer('Выбери, что хочешь посетить:  👀', reply_markup=events_kb)

# отправление инлайн-кнопок со ссылками на соцсети
@basic_router.message(F.text == 'Наши соцсети ✉')
async def url_command(message: types.Message):
    await message.answer(
        'Выберите соцсеть',
        reply_markup=builder)

# отправление списка доступных команд, для админовых и простых смертных соответственно 
@basic_router.message(Command('commands'))
async def send_commands(message: types.Message):
    if message.from_user.id in admin_id:
        commands_text = "Команды, которыми Вы можете воспользоваться:\n\n/users - количество новых пользователей\n\n/url - количество новых пользователей, перешедших по ссылке\n\n/file - количество пользователей, которые нажали на кнопку запроса файла программы ДОД\n\n/network - количество новых пользователей перешедших по кнопке на соцсети\n/newbutton - добавить новую кнопку в список мероприятий\n/deletebutton - удалить кнопку из списка мероприятий"
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


# отмена действия
@basic_router.callback_query(F.data == "cancel_action")
async def cancel_action(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.answer(text = "Действие отменено")
    await callback_query.answer()
    await asyncio.sleep(1)
    await callback_query.message.delete()

#region FSM Удаление кнопки

@basic_router.message(Command('deletebutton'), StateFilter(None))
async def cmd_deletebutton(message: types.Message, state: FSMContext):
    if message.from_user.id not in admin_id: return
    await message.answer(text = "Нажмите для отмены действия", reply_markup = cancel_menu)

    buttons = load_data()
    inner_kb = InlineKeyboardMarkup(inline_keyboard=[], resize_keyboard=True)
    for i in buttons["events"]:
        if i['has_inner'] == False:
            inner_kb.inline_keyboard.append([InlineKeyboardButton(text = i['header'] + ' ❌', callback_data = f"generic_deletebutton_{i['key']}")])
        else:
            inner_kb.inline_keyboard.append([InlineKeyboardButton(text = i['header'] + ' ➡️', callback_data = f"generic_deletebutton_{i['key']}")])
    await message.answer(text = "Веберите, кнопку для удаления:", reply_markup = inner_kb)

@basic_router.callback_query(F.data.regexp(r"generic_deletebutton_(.+)"))
async def deletebutton_choosing_layer(callback_query: types.CallbackQuery, state: FSMContext):
    buttons = load_data()
    event_key = callback_query.data.split('_')[2]
    btn = find_button_by_key(buttons['events'], event_key)
    inner_kb = InlineKeyboardMarkup(inline_keyboard=[], resize_keyboard=True)

    if btn['has_inner'] == True:
        for i in btn["inner_kb"]:
            if i['has_inner'] == False:
                inner_kb.inline_keyboard.append([InlineKeyboardButton(text = i['header'] + ' ❌', callback_data = f"generic_deletebutton_{i['key']}")])
            else:
                inner_kb.inline_keyboard.append([InlineKeyboardButton(text = i['header'] + ' ➡️', callback_data = f"generic_deletebutton_{i['key']}")])
        inner_kb.inline_keyboard.append([InlineKeyboardButton(text = "🗑️ Удалить весь подпункт 🗑️", callback_data = f"generic_deletebutton-menu_{btn['key']}")])
        inner_kb.inline_keyboard.append([InlineKeyboardButton(text = "🏠 Вернуться на главную", callback_data = "return_to_deletebutton_root")])
        await callback_query.message.edit_reply_markup(reply_markup = inner_kb)
    else:
        event_key = callback_query.data.split('_')[2]

        await state.update_data(source = event_key)
        await state.set_state(DeleteButtonForm.deleting)
        deleting_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="delete_yes"),
            InlineKeyboardButton(text="Нет", callback_data="delete_no")]
        ], resize_keyboard = True)
        await callback_query.message.answer("Вы уверены что хотите удалить эту кнопку?", reply_markup=deleting_kb)
    await callback_query.answer()

@basic_router.callback_query(F.data == "return_to_deletebutton_root")
async def return_to_deletebutton_root(callback_query: types.CallbackQuery, state: FSMContext):
    buttons = load_data()
    inner_kb = InlineKeyboardMarkup(inline_keyboard=[], resize_keyboard=True)
    for i in buttons["events"]:
        if i['has_inner'] == False:
            inner_kb.inline_keyboard.append([InlineKeyboardButton(text = i['header'] + ' ❌', callback_data = f"generic_deletebutton_{i['key']}")])
        else:
            inner_kb.inline_keyboard.append([InlineKeyboardButton(text = i['header'] + ' ➡️', callback_data = f"generic_deletebutton_{i['key']}")])
    await callback_query.message.edit_reply_markup(reply_markup = inner_kb)
    await callback_query.answer()

@basic_router.callback_query(F.data.regexp(r"generic_deletebutton-menu_(.+)"))
async def deletebuttonmenu_choosing_layer(callback_query: types.CallbackQuery, state: FSMContext):
    event_key = callback_query.data.split('_')[2]

    await state.update_data(source = event_key)
    await state.set_state(DeleteButtonForm.deleting)
    deleting_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="delete_yes"),
        InlineKeyboardButton(text="Нет", callback_data="delete_no")]
    ], resize_keyboard = True)
    await callback_query.message.answer("Вы уверены что хотите безвозвратно удалить весь подпункт?", reply_markup=deleting_kb)

@basic_router.callback_query(DeleteButtonForm.deleting, F.data == "delete_yes")
async def deletebutton_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    data = load_data()
    state_data = await state.get_data()
    button_key = state_data['source']
    
    if delete_button(data['events'], button_key):
        await callback_query.answer(f"Кнопка или подпункт '{button_key}' удалена.", reply_markup = startkb)
        await callback_query.message.delete()
    else:
        await callback_query.answer(f"Не удалось найти или удалить кнопку '{button_key}'.", reply_markup = startkb)
        await callback_query.message.delete()
    save_data(data)
    await state.clear()

@basic_router.callback_query(DeleteButtonForm.deleting, F.data == "delete_no")
async def deletebutton_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.answer(text = "Действие отменено")
    await callback_query.answer()
    await asyncio.sleep(1)
    await callback_query.message.delete()

#endregion

#region FSM Добавление новой кнопки -------------------------------- 

@basic_router.message(Command('newbutton'), StateFilter(None))
async def cmd_newbutton(message: types.Message, state: FSMContext):
    if message.from_user.id not in admin_id: return
    await message.answer(text = "Нажмите для отмены действия", reply_markup = cancel_menu)

    buttons = load_data()
    inner_kb = InlineKeyboardMarkup(inline_keyboard=[], resize_keyboard=True)
    for i in buttons["events"]:
        if i['has_inner'] == False:
            inner_kb.inline_keyboard.append([InlineKeyboardButton(text = i['header'], callback_data = f"generic_newbutton_{i['key']}")])
        else:
            inner_kb.inline_keyboard.append([InlineKeyboardButton(text = i['header'] + ' ➡️', callback_data = f"generic_newbutton_{i['key']}")])
    inner_kb.inline_keyboard.append([InlineKeyboardButton(text = "➕ Добавить кнопку", callback_data = "create_newbutton_root")])
    inner_kb.inline_keyboard.append([InlineKeyboardButton(text = "➕➡️ Добавить подпункт", callback_data = f"create_newbutton-menu_root")])
    await message.answer(text = "Веберите, куда добавить новую кнопку:", reply_markup = inner_kb)
    

@basic_router.callback_query(F.data.regexp(r"generic_newbutton_(.+)"))
async def newbutton_choosing_layer(callback_query: types.CallbackQuery, state: FSMContext):
    buttons = load_data()
    event_key = callback_query.data.split('_')[2]
    btn = find_button_by_key(buttons['events'], event_key)
    inner_kb = InlineKeyboardMarkup(inline_keyboard=[], resize_keyboard=True)

    if btn['has_inner'] == False:
        await callback_query.answer(text = "У этой кнопки нет внутреннего меню")
    else:
        for i in btn["inner_kb"]:
            if i['has_inner'] == False:
                inner_kb.inline_keyboard.append([InlineKeyboardButton(text = i['header'], callback_data = f"generic_newbutton_{i['key']}")])
            else:
                inner_kb.inline_keyboard.append([InlineKeyboardButton(text = i['header'] + ' ➡️', callback_data = f"generic_newbutton_{i['key']}")])
        inner_kb.inline_keyboard.append([InlineKeyboardButton(text = "➕ Добавить кнопку", callback_data = f"create_newbutton_{event_key}")])
        inner_kb.inline_keyboard.append([InlineKeyboardButton(text = "➕➡️ Добавить подпункт", callback_data = f"create_newbutton-menu_{event_key}")])
        inner_kb.inline_keyboard.append([InlineKeyboardButton(text = "🏠 Вернуться на главную", callback_data = "return_to_newbutton_root")])
        await callback_query.message.edit_reply_markup(reply_markup = inner_kb)
    await callback_query.answer()


@basic_router.callback_query(F.data == "return_to_newbutton_root")
async def return_to_newbutton_root(callback_query: types.CallbackQuery, state: FSMContext):
    buttons = load_data()
    inner_kb = InlineKeyboardMarkup(inline_keyboard=[], resize_keyboard=True)
    for i in buttons["events"]:
        if i['has_inner'] == False:
            inner_kb.inline_keyboard.append([InlineKeyboardButton(text = i['header'], callback_data = f"generic_newbutton_{i['key']}")])
        else:
            inner_kb.inline_keyboard.append([InlineKeyboardButton(text = i['header'] + ' ➡️', callback_data = f"generic_newbutton_{i['key']}")])
    inner_kb.inline_keyboard.append([InlineKeyboardButton(text = "➕ Добавить кнопку", callback_data = "create_newbutton_root")])
    inner_kb.inline_keyboard.append([InlineKeyboardButton(text = "➕➡️ Добавить подпункт", callback_data = f"create_newbutton-menu_root")])
    
    await callback_query.message.edit_reply_markup(reply_markup=inner_kb)
    await callback_query.answer()

# новая кнопка-подменю
@basic_router.callback_query(F.data.regexp(r"create_newbutton-menu_(.+)"))
async def newbutton_menu_choosing_layer(callback_query: types.CallbackQuery, state: FSMContext):
    event_key = callback_query.data.split('_')[2]

    await state.update_data(source = event_key)
    await state.set_state(AddNewMenuButtonForm.reading_header)
    await callback_query.message.answer("Что будет написано на кнопке?")
    await callback_query.answer()

@basic_router.message(AddNewMenuButtonForm.reading_header, F.text)
async def newbutton_menu_choosing_header(message: types.Message, state: FSMContext):
    await state.update_data(header = message.text)
    await state.set_state(AddNewMenuButtonForm.reading_message)
    await message.answer("Теперь, определимся, что будет написано в ответном сообщении\n\n Напиши \'-\', если без сообщения", reply_markup = emptyfieldkb)

@basic_router.message(AddNewMenuButtonForm.reading_message, F.text)
async def newbutton_menu_choosing_message(message: types.Message, state: FSMContext):
    await state.update_data(message = message.text)
    data = await state.get_data()

    event_key = data['source']

    if data['message'] == "-": data['message'] = ""

    new_button = {
        "key" : f"{datetime.now()}",
        "has_inner" : True,
        "header" : data['header'],
        "message" : data['message'],
        "query" : "",
        "inner_kb" : []
    }

    kb_data = load_data()
    if event_key == "root":
        kb_data['events'].append(new_button)
        await message.answer("Кнопка успешно добавлена!", reply_markup = startkb)
    elif add_button(kb_data['events'], event_key, new_button):
        await message.answer("Кнопка успешно добавлена!", reply_markup = startkb)
    else:
        await message.answer("При добавлении произошла ошибка", reply_markup = startkb)
    save_data(kb_data)
    await state.clear()

# новая кнопка-действие
@basic_router.callback_query(F.data.regexp(r"create_newbutton_(.+)"))
async def newbutton_choosing_layer(callback_query: types.CallbackQuery, state: FSMContext):
    event_key = callback_query.data.split('_')[2]

    await state.update_data(source = event_key)
    await state.set_state(AddNewButtonForm.reading_header)
    await callback_query.message.answer("Что будет написано на кнопке?")
    await callback_query.answer()

@basic_router.message(AddNewButtonForm.reading_header, F.text)
async def newbutton_choosing_header(message: types.Message, state: FSMContext):
    await state.update_data(header = message.text)
    await state.set_state(AddNewButtonForm.reading_message)
    await message.answer("Теперь, определимся, что будет написано в ответном сообщении\n\n Напиши \'-\', если без сообщения", reply_markup = emptyfieldkb)

@basic_router.message(AddNewButtonForm.reading_message, F.text)
async def newbutton_choosing_message(message: types.Message, state: FSMContext):
    await state.update_data(message = message.text)
    await state.set_state(AddNewButtonForm.reading_query)
    await message.answer("И самое сложное - запрос к БД. Пример запроса:\n\nSELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 1\n\nНапиши \'-\', если без сообщения")

@basic_router.message(AddNewButtonForm.reading_query, F.text)
async def newbutton_choosing_query(message: types.Message, state: FSMContext):
    await state.update_data(query = message.text) 
    data = await state.get_data()

    event_key = data['source']

    if data['query'] == "-": data['query'] = ""
    if data['message'] == "-": data['message'] = ""

    new_button = {
        "key" : f"{datetime.now()}",
        "has_inner" : False,
        "header" : data['header'],
        "message" : data['message'],
        "query" : data['query']
    }

    kb_data = load_data()
    if event_key == "root":
        kb_data['events'].append(new_button)
        await message.answer("Кнопка успешно добавлена!", reply_markup = startkb)
    elif add_button(kb_data['events'], event_key, new_button):
        await message.answer("Кнопка успешно добавлена!", reply_markup = startkb)
    else:
        await message.answer("При добавлении произошла ошибка", reply_markup = startkb)
    save_data(kb_data)
    await state.clear()

#endregion

# универсальный обработчик кнопок 
@basic_router.callback_query(F.data.regexp(r"generic_(.+)"))
async def handle_generic_event_kb(callback_query: types.CallbackQuery):
    event_key = callback_query.data.split('_')[1]
    kb_buttons = json.loads(codecs.open('kb.json', "r", "utf_8_sig").read())
    message = ""
    query = ""
    has_inner = False
    inner_kb = InlineKeyboardMarkup(inline_keyboard=[], resize_keyboard=True)

    btn = find_button_by_key(kb_buttons['events'], event_key)
    if "inner_kb" in btn:
        has_inner = True
        for i in btn["inner_kb"]:
            inner_kb.inline_keyboard.append([InlineKeyboardButton(text = i['header'], callback_data = f"generic_{i['key']}")])
            
    message = btn['message']
    query = btn['query']
          
    if message != "": 
        if has_inner:
            await bot.send_message(callback_query.from_user.id, message, reply_markup=inner_kb)
        else:
            await bot.send_message(callback_query.from_user.id, message)
    if query != "": 
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            fotka, innffaa, fcam, map = result
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
