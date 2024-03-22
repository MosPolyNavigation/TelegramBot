from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# создание инлайн кнопок для выбора мероприятия ДОДа
urlkb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Официальная часть', callback_data='v1')],
    [InlineKeyboardButton(text='Мастер-классы', callback_data='v2')],
    [InlineKeyboardButton(text='Приёмная комиссия', callback_data='v3')],
    [InlineKeyboardButton(text='Выставка проектов', callback_data='v4')],
    [InlineKeyboardButton(text='Выставочная зона', callback_data='v5')],
    [InlineKeyboardButton(text='Бизнес-зона', callback_data='v6')],
    [InlineKeyboardButton(text='Паблик-толк с\nИгорем Асановым', callback_data='v7')],
    [InlineKeyboardButton(text='Несекретные материалы', callback_data='v8')],
    [InlineKeyboardButton(text='Стенды информации', callback_data='v9')],
    [InlineKeyboardButton(text='Викторины', callback_data='v11')],
    [InlineKeyboardButton(text='Квест "Зачетка абитуриента"', callback_data='v12')],
    [InlineKeyboardButton(text='Художественная школа "Полиграф"', callback_data='v13')],
    [InlineKeyboardButton(text='Киберспортивные танцы', callback_data='v14')]
    # [InlineKeyboardButton(text='WorkShop', callback_data='v10')]
], resize_keyboard=True)

# Если выбор пал на офиц часть
inmkb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Арт, дизайн и медиа', callback_data='m1')],
    [InlineKeyboardButton(text='Урбанистика', callback_data='m2')],
    [InlineKeyboardButton(text='Бизнес', callback_data='m4')],
    [InlineKeyboardButton(text='Информационные технологии', callback_data='m5')],
    [InlineKeyboardButton(text='Транспорт, цифра, логистика', callback_data='m6')],
    [InlineKeyboardButton(text='Экология и технологии жизни', callback_data='m3')],
    [InlineKeyboardButton(text='Технологии, материалы и производство', callback_data='m7')],
], resize_keyboard=True)

# Если выбор пал на офиц часть
inkb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Официальная часть в А200', callback_data='w1')],
    # [InlineKeyboardButton(text='Трансляция официальной части', callback_data='w4')],
    [InlineKeyboardButton(text='Встреча с деканом факультета', callback_data='w2')],
    [InlineKeyboardButton(text='Встреча с директором института', callback_data='w3')],
], resize_keyboard=True)

inwkb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Машиностроение', callback_data='ww1')],
    [InlineKeyboardButton(text='Урбанистика и \n'
                               'городское хозяйство', callback_data='ww2')],
    [InlineKeyboardButton(text='Химические технологии \n'
                               'и беотехнологии', callback_data='ww3')],
    [InlineKeyboardButton(text='Экономика и управление', callback_data='ww4')],
    [InlineKeyboardButton(text='Информационные технологии', callback_data='ww5')],
    [InlineKeyboardButton(text='Транспортный факультет', callback_data='ww6')],
], resize_keyboard=True)

ynwkb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Полиграфический институт', callback_data='yw1')],
    [InlineKeyboardButton(text='Институт графики и искусства\nкниги имении В.А. Фаворского', callback_data='yw2')],
    [InlineKeyboardButton(text='Институт издательского дела\nи журналистики', callback_data='yw3')],
], resize_keyboard=True)

# Стандартная клавиатура
startkb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Новый маршрут 📌')],
    [KeyboardButton(text='Библиотека карт 🗺', web_app=WebAppInfo(url='https://mospolynavigation.github.io/dod/'))],
    [KeyboardButton(text='Наши соцсети ✉')],
    [KeyboardButton(text='Программа ДОД 📄')]
], resize_keyboard=True)

builder = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="VK", url="https://vk.com/mospolynavigation")],
    [InlineKeyboardButton(text="Telegram", url="https://t.me/mospolynavigation")]
], resize_keyboard=True)
