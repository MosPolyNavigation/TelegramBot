
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

#создание инлайн кнопок для выбора мероприятия ДОДа
urlkb = InlineKeyboardMarkup(inline_keyboard= [
        [InlineKeyboardButton(text='Маршрут до кампуса', callback_data='campus')],
        [InlineKeyboardButton(text='Маршрут до аудитории', callback_data='auditorium')],
        [InlineKeyboardButton(text='Маршрут до точки интереса', callback_data='pointinterest')],
], resize_keyboard = True)

# Если выбор пал на кампус
mapcampus =  InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton(text='Большая Семёновская, 38',  url='https://t.me/mospolyna_bot/Bolshaya_Semyonovskaya')],
        [InlineKeyboardButton(text='Автозаводская, 16', url='https://t.me/mospolyna_bot/Avtozavodskaya')],
        [InlineKeyboardButton(text='Михалковская, 7', url='https://t.me/mospolyna_bot/Mikhalkovskaya')],
        [InlineKeyboardButton(text='Прянишкова, 2А', url='https://t.me/mospolyna_bot/pryanishkova')],
        [InlineKeyboardButton(text='Павла Корчагина, 22', url='https://t.me/mospolyna_bot/Pavel_Korchagin')],
], row_width=1, resize_keyboard = True)

# Если выбор пал на точку интереса
map_pointinterest =  InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton(text='Большая Семёновская, 38', callback_data='pointinterestBS')],
        [InlineKeyboardButton(text='Автозаводская, 16', callback_data='pointinterestAv')],
        [InlineKeyboardButton(text='Михалковская, 7', callback_data='pointinterestM')],
        [InlineKeyboardButton(text='Прянишкова, 2А', callback_data='pointinterestPr')],
        [InlineKeyboardButton(text='Павла Корчагина, 22', callback_data='pointinterestPK')],
], resize_keyboard = True)

#точки интереса БС (временно так)
map_BS =  InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton(text='Административные отделы:  📑  💸  🏫  ', callback_data='BS1')],
        [InlineKeyboardButton(text='Общественные помещения:  📚  🥣  🚻  ', callback_data='BS3')],
        [InlineKeyboardButton(text='Развлечения  и  отдых:   🛌   🎭   💪', callback_data='BS2')],
], resize_keyboard = True)

# Стандартная клавиатура
startkb = ReplyKeyboardMarkup( keyboard=[
        [KeyboardButton(text='Новый маршрут 📌')],
        [KeyboardButton(text='Наши соцсети ✉')]
], resize_keyboard=True)

builder = InlineKeyboardMarkup(inline_keyboard= [
        [InlineKeyboardButton(text="VK", url="https://vk.com/mospolynavigation")],
        [InlineKeyboardButton(text="Telegram", url="https://t.me/mospolynavigation")]
], resize_keyboard=True)