from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from messages import notinfa, okbs3, okbs1, okbs2, okbs5, okbs6, okbs7, okbs8, okbs9, oka1, oka2, oka3, oka4, oka5, oka6, oka7, okm1, okm2, okm3, okm4, okm5, okpr1, okpr2, okpr3, okpr4, okpr5, okpr6, okpk1, okpk2, okpk3, okpk4, okpk5, okpk6

import sqlite3
import re

conn = sqlite3.connect('mybazed.db')
cursor = conn.cursor()

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton #ReplyKeyboardRemove


TOKEN = '5895809940:AAENleKqlA8yA-9Tbh5j6VDIbnmCbPkHx80'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


async def on_startup(_):
	print('Бот вышел в онлайн')


# команда старт
@dp.message_handler(commands=['start'])
async def commands_start(message: types.Message):
	# Создаем клавиатуру для выбора языка
	keyboard = InlineKeyboardMarkup(row_width=2)
	button_rus = InlineKeyboardButton(text='English', callback_data='language_en')
	button_eng = InlineKeyboardButton(text='Русский', callback_data='language_ru')
	keyboard.add(button_eng, button_rus)

	await message.answer('Выберите язык / Choose language:', reply_markup=keyboard)


# инлайн-кнопки
@dp.callback_query_handler(lambda c: c.data in ['language_en', 'language_ru'])
async def handle_language(callback_query: types.CallbackQuery):
    language = callback_query.data

    if language == 'language_ru':
        # Создаем клавиатуру с кнопкой "НовыйМаршрут"
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        button_new_marshrut = KeyboardButton('НовыйМаршрут')
        keyboard.add(button_new_marshrut)

        await callback_query.answer()
        await callback_query.message.answer('Чтобы продолжить, нажмите на кнопку «НовыйМаршрут».', reply_markup=keyboard)

    elif language == 'language_en':
        # создаем клавиатуру с кнопкой "NewRoute" на английском языке
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        button_new_route = KeyboardButton('NewRoute')
        keyboard.add(button_new_route)

        # отправляем сообщение с предложением создать новый маршрут и клавиатурой на английском языке
        await callback_query.answer()
        await callback_query.message.answer('To continue, click on the «NewRoute» button.', reply_markup=keyboard)





#команда узнать маршрут и выбор кнопок аудитории и точки интереса
urlkb = InlineKeyboardMarkup(row_width=1)
urlButton1 = InlineKeyboardButton(text='Маршрут до аудитории', callback_data='v1')
urlButton2 = InlineKeyboardButton(text='Маршрут до точки интереса', callback_data='v2')
urlButton3 = InlineKeyboardButton(text='Маршрут до кампуса', callback_data='v3')
urlButton4 = InlineKeyboardButton(text='Внеучебная деядельность', callback_data='v4')
urlkb.add(urlButton3, urlButton1, urlButton2, urlButton4)

@dp.message_handler(lambda message: message.text == 'НовыйМаршрут')
async def url_command(message : types.Message):
	await message.answer('Что Вы хотите узнать?  👀', reply_markup=urlkb)


#тоже самое только на английском
en = InlineKeyboardMarkup(row_width=1)
enButton1 = InlineKeyboardButton(text='Route to the auditorium', callback_data='en1')
enButton2 = InlineKeyboardButton(text='Route to the point of interest', callback_data='en2')
enButton3 = InlineKeyboardButton(text='Route to the campus', callback_data='en3')
enButton4 = InlineKeyboardButton(text='Внеучебная деядельность', callback_data='en4')
en.add(enButton1, enButton2, enButton3, enButton4)

@dp.message_handler(lambda message: message.text == 'NewRoute')
async def en_command(message : types.Message):
	await message.answer('What do you want to know?  👀', reply_markup=en)



@dp.callback_query_handler(lambda callback_query: callback_query.data == 'v4')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Внеучебная деятельность»')
    await bot.send_message(callback_query.from_user.id, okbs9, parse_mode="HTML")
    await bot.send_message(callback_query.from_user.id, oka7, parse_mode="HTML")
    await bot.send_message(callback_query.from_user.id, okm5, parse_mode="HTML")
    await bot.send_message(callback_query.from_user.id, okpk6, parse_mode="HTML")
    await bot.answer_callback_query(callback_query.id)


#вывод после выбора кнопки АУДИТОРИИ
@dp.callback_query_handler(text='v1')
async def first_function(callback : types.CallbackQuery):
	await callback.message.answer('Введите номер нужной аудитории в формате, который указан в Вашем расписании.\nНомер аудитории должен содержать буквенные символы, которые обозначают название кампуса, а также численные символы (4 цифры)\n\nПример ввода: АВ1407 \n"АВ"- обозначение кампуса на Автозаводской,\n"1" - корпус, "4" - этаж, "07" - аудитория.\n(На данный момент доступен первый корпус на ул.Автозаводская)')
	await callback.answer()


@dp.callback_query_handler(text='en1')
async def first_function(callback : types.CallbackQuery):
	await callback.message.answer('Enter the number of the required auditorium in the format specified in your schedule.\nThe auditorium number must contain alphabetic characters that denote the name of the campus, as well as numeric characters (4 digits).\n\nInput example: AB1407 \n"AB" - the designation of the campus at Avtozavodskaya, \n"1" - building, "4" - floor, "07" - auditorium.')
	await callback.answer()

# функция для базы данных с аудиториями
@dp.message_handler()
async def second_function(message: types.Message):
	global is_first_function_completed
	if is_first_function_completed:
		room = message.text.strip().upper()#приводим текст к верхнему регистру и убираем пробелы между символами


		query = "SELECT infa, fotka FROM Auditoriums WHERE room_number = ?"
		cursor.execute(query, (room,))
		row = cursor.fetchone()

		if re.match(r'^[а-яА-Я]{1,2}\d{4}$', room):
			if row is not None:
				infa, fotka = row
				await message.reply(f"{infa}")
				await bot.send_photo(chat_id=message.chat.id, photo=fotka)
			else:
				await message.reply(f"Информация о маршруте до аудитории {room} не найдена.")
		else:
			await message.answer('Номер аудитории был введён некорректно.\nПовторите попытку.')

#вывод после выбора кнопки ТОЧКИ ИНТЕРЕСА
@dp.callback_query_handler(text='v2')
async def v2_call(callback : types.CallbackQuery):
	await callback.message.answer('По какому адресу Вы сейчас находитесь?', reply_markup=inkb)
	await callback.answer()

@dp.callback_query_handler(text='en2')
async def v2_call(callback : types.CallbackQuery):
	await callback.message.answer('What address are you currently at?', reply_markup=inkben)
	await callback.answer()

#вывод после выбора кнопки КАМПУСА
@dp.callback_query_handler(text='v3')
async def v3_call(callback : types.CallbackQuery):
	await callback.message.answer('Какой кампус Вам нужен?', reply_markup=inkam)
	await callback.answer()

@dp.callback_query_handler(text='en3')
async def v3_call(callback : types.CallbackQuery):
	await callback.message.answer('Which campus do you need?', reply_markup=inkam)
	await callback.answer()


#Маршрут до точки интереса
inkb = InlineKeyboardMarkup(row_width=1)
kampus1 = InlineKeyboardButton(text='ул. Большая Семёновская, д. 38', callback_data='w1')
kampus2 = InlineKeyboardButton(text='ул. Автозаводская, д. 16', callback_data='w2')
kampus3 = InlineKeyboardButton(text='ул. Михалковская, д. 7', callback_data='w3')
kampus4 = InlineKeyboardButton(text='ул. Прянишкова, 2А', callback_data='w4')
kampus5 = InlineKeyboardButton(text='ул. Павла Корчагина, д. 22', callback_data='w5')
inkb.add(kampus1, kampus2, kampus3, kampus4, kampus5)

@dp.message_handler(commands='test')
async def test_command(message : types.Message):
	await message.answer('По какому адресу Вы сейчас находитесь?', reply_markup=inkb)

#Маршрут до точки интереса en
inkben = InlineKeyboardMarkup(row_width=1)
kampus1 = InlineKeyboardButton(text='Bolshaya Semyonovskaya str., 38', callback_data='e1')
kampus2 = InlineKeyboardButton(text='Avtozavodskaya str., 16', callback_data='e2')
kampus3 = InlineKeyboardButton(text='Mikhalkovskaya str., 7', callback_data='e3')
kampus4 = InlineKeyboardButton(text='Pryanishnikova str., 2А', callback_data='e4')
kampus5 = InlineKeyboardButton(text='Pavel Korchagin str., 22', callback_data='e5')
inkben.add(kampus1, kampus2, kampus3, kampus4, kampus5)

@dp.message_handler(commands='teste')
async def test_command(message: types.Message):
	await message.answer('What address are you currently at?', reply_markup=inkben)


#Точки интереса на БС
@dp.callback_query_handler(text='w1')
async def w1_call(callback : types.CallbackQuery):
	await callback.message.answer('Вы выбрали кампус на Большой Семёновской,\n "БС"-обозначение в Вашем расписании.')
	await callback.message.answer('Выберите, что вы хотите посетить:', reply_markup=tochka1)
	await callback.answer()

@dp.callback_query_handler(text='e1')
async def w1_call(callback : types.CallbackQuery):
	await callback.message.answer('You have chosen a campus on Bolshaya Semenovskaya,\n "БС" is the designation in your schedule.')
	await callback.message.answer('Choose what you want to visit:', reply_markup=tochkae1)
	await callback.answer()

tochka1 = InlineKeyboardMarkup(row_width=1)
tbs1 = InlineKeyboardButton(text='Зона отдыха', callback_data='tok1')
tbs2 = InlineKeyboardButton(text='Кабинет редкой книги', callback_data='tok2')
tbs3 = InlineKeyboardButton(text='Выставочные залы', callback_data='tok3')
tbs5 = InlineKeyboardButton(text='МФЦ', callback_data='tok5')
tbs6 = InlineKeyboardButton(text='Столовая', callback_data='tok6')
tbs7 = InlineKeyboardButton(text='Медпункт', callback_data='tok7')
tbs8 = InlineKeyboardButton(text='Лаборатории', callback_data='tok8')
tbs9 = InlineKeyboardButton(text='Внеучебная деятельность', callback_data='tok9')
tochka1.add(tbs1, tbs5, tbs6, tbs7, tbs8, tbs3, tbs2, tbs9)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tok3')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Выставочные залы»')
    await bot.send_message(callback_query.from_user.id, okbs3)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tok1')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Зона отдыха»')
    await bot.send_message(callback_query.from_user.id, okbs1)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tok2')
async def handle_tok2(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Кабинет редкой книги»')
    await bot.send_message(callback_query.from_user.id, okbs2)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tok5')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «МФЦ»')
    await bot.send_message(callback_query.from_user.id, okbs5)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tok6')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Столовая»')
    await bot.send_message(callback_query.from_user.id, okbs6)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tok7')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Медпункт»')
    await bot.send_message(callback_query.from_user.id, okbs7)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tok8')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Лаборатории»')
    await bot.send_message(callback_query.from_user.id, okbs8, parse_mode="HTML")
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tok9')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Внеучебная деятельность»')
    await bot.send_message(callback_query.from_user.id, okbs9, parse_mode="HTML")
    await bot.answer_callback_query(callback_query.id)


tochkae1 = InlineKeyboardMarkup(row_width=1)
tbse1 = InlineKeyboardButton(text='Recreation area', callback_data='toke1')
tbse2 = InlineKeyboardButton(text='Cabinet of a rare book', callback_data='toke2')
tbse3 = InlineKeyboardButton(text='Exhibition halls', callback_data='toke3')
tbse5 = InlineKeyboardButton(text='MFC', callback_data='toke5')
tbse6 = InlineKeyboardButton(text='Lunch hall', callback_data='toke6')
tbse7 = InlineKeyboardButton(text='Medical center', callback_data='toke7')
tbse8 = InlineKeyboardButton(text='Laboratories', callback_data='toke8')
tbse9 = InlineKeyboardButton(text='Extracurricular activities', callback_data='toke9')
tochkae1.add(tbse1, tbse5, tbse6, tbse7, tbse8, tbse3, tbse2, tbse9)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'toke3')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Exhibition halls»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'toke1')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Recreation area»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'toke2')
async def handle_tok2(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Cabinet of a rare book»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'toke5')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «MFC»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'toke6')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Lunch hall»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'toke7')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Medical center»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'toke8')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Laboratories»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'toke9')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Extracurricular activities»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.message_handler(commands='tochkamoi')
async def tochka_command(message: types.Message):
	await message.answer('Выберите, что Вы хотите посетить:', reply_markup=tochka1)

@dp.message_handler(commands='tochkamoie')
async def tochka_command(message: types.Message):
	await message.answer('Choose what you want to visit:', reply_markup=tochkae1)




#точки интереса на АВ

@dp.callback_query_handler(text='w2')
async def w2_call(callback : types.CallbackQuery):
	await callback.message.answer('Вы выбрали кампус на Автозаводской,\n "АВ"-обозначение в Вашем расписании.')
	await callback.message.answer('Выберите, что Вы хотите посетить:', reply_markup=tochka2)
	await callback.answer()

@dp.callback_query_handler(text='e2')
async def e1_call(callback : types.CallbackQuery):
	await callback.message.answer('You have chosen a campus on Avtozavodskaya,\n "AB" is the designation in your schedule.')
	await callback.message.answer('Choose what you want to visit:', reply_markup=tochkae2)
	await callback.answer()


tochka2 = InlineKeyboardMarkup(row_width=1)
ta1 = InlineKeyboardButton(text='Зоны отдыха', callback_data='toka1')
ta2 = InlineKeyboardButton(text='«Арт-политех»', callback_data='toka2')
ta3 = InlineKeyboardButton(text='МФЦ', callback_data='toka3')
ta4 = InlineKeyboardButton(text='Библиотека', callback_data='toka4')
ta5 = InlineKeyboardButton(text='Столовая', callback_data='toka5')
ta6 = InlineKeyboardButton(text='Лаборатории', callback_data='toka6')
ta7 = InlineKeyboardButton(text='Внеучебная деятельность', callback_data='toka7')
tochka2.add(ta1, ta2, ta3, ta4, ta5, ta6, ta7)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'toka3')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «МФЦ»')
    await bot.send_message(callback_query.from_user.id, oka3)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'toka1')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Зона отдыха»')
    await bot.send_message(callback_query.from_user.id, oka1)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'toka2')
async def handle_tok2(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Арт-политех»')
    await bot.send_message(callback_query.from_user.id, oka2)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'toka4')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Библиотека»')
    await bot.send_message(callback_query.from_user.id, oka4)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'toka5')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Столовая»')
    await bot.send_message(callback_query.from_user.id, oka5)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'toka6')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Лаборатории»')
    await bot.send_message(callback_query.from_user.id, oka6, parse_mode="HTML")
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'toka7')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Внеучебная деятельность»')
    await bot.send_message(callback_query.from_user.id, oka7, parse_mode="HTML")
    await bot.answer_callback_query(callback_query.id)

tochkae2 = InlineKeyboardMarkup(row_width=1)
tae1 = InlineKeyboardButton(text='Recreation area', callback_data='tokae1')
tae2 = InlineKeyboardButton(text='«Artpolitics»', callback_data='tokae2')
tae3 = InlineKeyboardButton(text='MFC', callback_data='tokae3')
tae4 = InlineKeyboardButton(text='Library', callback_data='tokae4')
tae5 = InlineKeyboardButton(text='Lunch hall', callback_data='tokae5')
tae6 = InlineKeyboardButton(text='Laboratories', callback_data='tokae6')
tae7 = InlineKeyboardButton(text='Extracurricular activities', callback_data='tokae7')
tochkae2.add(tae1, tae2, tae3, tae4, tae5, tae6, tae7)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokae3')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «MFC»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokae1')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Recreation area»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokae2')
async def handle_tok2(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Artpolitics»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokae4')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Library»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokae5')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Lunch hall»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokae6')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Laboratories»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokae7')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Extracurricular activities»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.message_handler(commands='tochkamoi')
async def tochka_command(message : types.Message):
	await message.answer('Выберите, что Вы хотите посетить:', reply_markup=tochka2)

@dp.message_handler(commands='tochkamoie')
async def tochka_command(message : types.Message):
	await message.answer('Choose what you want to visit:', reply_markup=tochkae2)

#точки интереса на М
@dp.callback_query_handler(text='w3')
async def w3_call(callback : types.CallbackQuery):
	await callback.message.answer('Вы выбрали кампус на Михалковской,\n"M"-обозначение в Вашем расписании.')
	await callback.message.answer('Выберите, что Вы хотите посетить:', reply_markup=tochka3)
	await callback.answer()

@dp.callback_query_handler(text='e3')
async def w3_call(callback : types.CallbackQuery):
	await callback.message.answer('You have chosen a campus on Mikhalkovskaya,\n "M" is the designation in your schedule.')
	await callback.message.answer('Choose what you want to visit:', reply_markup=tochkae3)
	await callback.answer()

tochka3 = InlineKeyboardMarkup(row_width=1)
tm1 = InlineKeyboardButton(text='Зона отдыха', callback_data='tokm1')
tm2 = InlineKeyboardButton(text='Музей', callback_data='tokm2')
tm3 = InlineKeyboardButton(text='Столовая', callback_data='tokm3')
tm4 = InlineKeyboardButton(text='Выставочные залы', callback_data='tokm4')
tm5 = InlineKeyboardButton(text='Внеучебная деятельность', callback_data='tokm5')
tochka3.add(tm1, tm2, tm3, tm4, tm5)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokm3')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Столовая»')
    await bot.send_message(callback_query.from_user.id, okm3)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokm1')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Зона отдыха»')
    await bot.send_message(callback_query.from_user.id, okm1)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokm2')
async def handle_tok2(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Музей»')
    await bot.send_message(callback_query.from_user.id, okm2)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokm4')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Выставочные залы»')
    await bot.send_message(callback_query.from_user.id, okm4)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokm5')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Внеучебная деятельность»')
    await bot.send_message(callback_query.from_user.id, okm5, parse_mode="HTML")
    await bot.answer_callback_query(callback_query.id)

tochkae3 = InlineKeyboardMarkup(row_width=1)
tme1 = InlineKeyboardButton(text='Recreation area', callback_data='tokme1')
tme2 = InlineKeyboardButton(text='Museum', callback_data='tokme2')
tme3 = InlineKeyboardButton(text='Lunch hall', callback_data='tokme3')
tme4 = InlineKeyboardButton(text='Exhibition halls', callback_data='tokme4')
tme5 = InlineKeyboardButton(text='Extracurricular activities', callback_data='tokme5')
tochkae3.add(tme1, tme2, tme3, tme4, tme5)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokme3')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Lunch hall»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokme1')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Recreation area»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokme2')
async def handle_tok2(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Museum»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokme4')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Exhibition halls»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokme5')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Extracurricular activities»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.message_handler(commands='tochkamoi')
async def tochka_command(message : types.Message):
	await message.answer('Выберите, что Вы хотите посетить:', reply_markup=tochka3)

@dp.message_handler(commands='tochkamoie')
async def tochka_command(message : types.Message):
	await message.answer('Choose what you want to visit:', reply_markup=tochkae3)


#точки интереса на ПР
@dp.callback_query_handler(text='w4')
async def w4_call(callback : types.CallbackQuery):
	await callback.message.answer('Вы выбрали кампус на Прянишкова,\n "ПР"-обозначение в Вашем расписании.')
	await callback.message.answer('Выберите, что Вы хотите посетить:', reply_markup=tochka4)
	await callback.answer()

@dp.callback_query_handler(text='e4')
async def w4_call(callback : types.CallbackQuery):
	await callback.message.answer('You have chosen a campus on Pryanishnikova,\n "ПР" is the designation in your schedule.')
	await callback.message.answer('Choose what you want to visit:', reply_markup=tochkae4)
	await callback.answer()


tochka4 = InlineKeyboardMarkup(row_width=1)
tpr1 = InlineKeyboardButton(text='Зона отдыха', callback_data='tokpr1')
tpr2 = InlineKeyboardButton(text='МФЦ', callback_data='tokpr2')
tpr3 = InlineKeyboardButton(text='Библиотека', callback_data='tokpr3')
tpr4 = InlineKeyboardButton(text='Буфет', callback_data='tokpr4')
tpr5 = InlineKeyboardButton(text='Музейная площадка', callback_data='tokpr5')
tpr6 = InlineKeyboardButton(text='Лаборатории', callback_data='tokpr6')
tochka4.add(tpr1, tpr2, tpr3, tpr4, tpr5, tpr6)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpr1')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Зона отдыха»')
    await bot.send_message(callback_query.from_user.id, okpr1)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpr2')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «МФЦ»')
    await bot.send_message(callback_query.from_user.id, okpr2, parse_mode="HTML")
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpr3')
async def handle_tok2(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Библиотека»')
    await bot.send_message(callback_query.from_user.id, okpr3)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpr4')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Буфет»')
    await bot.send_message(callback_query.from_user.id, okpr4)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpr5')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Музейная площадка»')
    await bot.send_message(callback_query.from_user.id, okpr5, parse_mode="HTML")
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpr6')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Лаборатории»')
    await bot.send_message(callback_query.from_user.id, okpr6, parse_mode="HTML")
    await bot.answer_callback_query(callback_query.id)

tochkae4 = InlineKeyboardMarkup(row_width=1)
tpre1 = InlineKeyboardButton(text='Recreation area', callback_data='tokpre1')
tpre2 = InlineKeyboardButton(text='MFC', callback_data='tokpre2')
tpre3 = InlineKeyboardButton(text='Library', callback_data='tokpre3')
tpre4 = InlineKeyboardButton(text='Buffet', callback_data='tokpre4')
tpre5 = InlineKeyboardButton(text='Museum site', callback_data='tokpre5')
tpre6 = InlineKeyboardButton(text='Laboratories', callback_data='tokpre6')
tochkae4.add(tpre1, tpre2, tpre3, tpre4, tpre5, tpre6)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpre1')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Recreation area»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpre2')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «MFC»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpre3')
async def handle_tok2(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Library»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpre4')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Buffet»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpre5')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Museum site»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpre6')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Laboratories»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.message_handler(commands='tochkamoi')
async def tochka_command(message : types.Message):
	await message.answer('Выберите, что Вы хотите посетить:', reply_markup=tochka4)

@dp.message_handler(commands='tochkamoie')
async def tochka_command(message : types.Message):
	await message.answer('Choose what you want to visit:', reply_markup=tochkae4)


#точки итереса на ПК
@dp.callback_query_handler(text='w5')
async def w5_call(callback : types.CallbackQuery):
	await callback.message.answer('Вы выбрали кампус на Павла Корчагина,\n "ПК"-обозначение в Вашем расписании.')
	await callback.message.answer('Выберите, что Вы хотите посетить:', reply_markup=tochka5)
	await callback.answer()

@dp.callback_query_handler(text='e5')
async def w5_call(callback : types.CallbackQuery):
	await callback.message.answer('You have chosen a campus on Pavel Korchagin,\n "ПК" is the designation in your schedule.')
	await callback.message.answer('Choose what you want to visit:', reply_markup=tochkae5)
	await callback.answer()

tochka5 = InlineKeyboardMarkup(row_width=1)
tpk1 = InlineKeyboardButton(text='Зона отдыха', callback_data='tokpk1')
tpk2 = InlineKeyboardButton(text='МФЦ', callback_data='tokpk2')
tpk3 = InlineKeyboardButton(text='Библиотека', callback_data='tokpk3')
tpk4 = InlineKeyboardButton(text='Столовая', callback_data='tokpk4')
tpk5 = InlineKeyboardButton(text='«Добро.Центр»', callback_data='tokpk5')
tpk6 = InlineKeyboardButton(text='Внеучебная деятельность', callback_data='tokpk6')
tochka5.add(tpk1, tpk5, tpk2, tpk3, tpk4, tpk6)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpk1')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Зона отдыха»')
    await bot.send_message(callback_query.from_user.id, okpk1)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpk2')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «МФЦ»')
    await bot.send_message(callback_query.from_user.id, okpk2, parse_mode="HTML")
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpk3')
async def handle_tok2(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Библиотека»')
    await bot.send_message(callback_query.from_user.id, okpk3)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpk4')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Столовая»')
    await bot.send_message(callback_query.from_user.id, okpk4)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpk5')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Добро.Центр»')
    await bot.send_message(callback_query.from_user.id, okpk5)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpk6')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы нажали на кнопку «Внеучебная деятельность»')
    await bot.send_message(callback_query.from_user.id, okpk6, parse_mode="HTML")
    await bot.answer_callback_query(callback_query.id)


tochkae5 = InlineKeyboardMarkup(row_width=1)
tpke1 = InlineKeyboardButton(text='Recreation area', callback_data='tokpke1')
tpke2 = InlineKeyboardButton(text='MFC', callback_data='tokpke2')
tpke3 = InlineKeyboardButton(text='Library', callback_data='tokpke3')
tpke4 = InlineKeyboardButton(text='Lunch hall', callback_data='tokpke4')
tpke5 = InlineKeyboardButton(text='«Goodness.Centre»', callback_data='tokpke5')
tpke6 = InlineKeyboardButton(text='Extracurricular activities', callback_data='tokpke6')
tochkae5.add(tpke1, tpke2, tpke3, tpke4, tpke5, tpke6)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpke1')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Recreation area»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpke2')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «MFC»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpke3')
async def handle_tok2(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Library»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpke4')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Lunch hall»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpke5')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Goodness.Centre»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'tokpke6')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'You clicked on the button «Extracurricular activities»')
    await bot.send_message(callback_query.from_user.id, notinfa)
    await bot.answer_callback_query(callback_query.id)

@dp.message_handler(commands='tochkamoi')
async def tochka_command(message : types.Message):
	await message.answer('Выберите, что Вы хотите посетить:', reply_markup=tochka5)

@dp.message_handler(commands='tochkamoie')
async def tochka_command(message : types.Message):
	await message.answer('Choose what you want to visit:', reply_markup=tochkae5)




#Маршрут до кампуса
inkam = InlineKeyboardMarkup(row_width=1)
kampus1 = InlineKeyboardButton(text='ул. Большая Семёновская, д. 38', url='https://yandex.ru/maps?rtext=55.824699%2C37.654953~55.781291%2C37.711518&rtt=mt')
kampus2 = InlineKeyboardButton(text='ул. Автозаводская, д. 16', url='https://yandex.ru/maps?rtext=55.781291%2C37.711518~55.70422%2C37.645196&rtt=mt')
kampus3 = InlineKeyboardButton(text='ул. Михалковская, д. 7', url='https://yandex.ru/maps?rtext=55.781291%2C37.711518~55.837459%2C37.533427&rtt=mt')
kampus4 = InlineKeyboardButton(text='ул. Прянишкова, 2А', url='https://yandex.ru/maps/-/CCUWz4eUGD')
kampus5 = InlineKeyboardButton(text='ул. Павла Корчагина, д. 22', url='https://yandex.ru/maps?rtext=55.781291%2C37.711518~55.819439%2C37.663351&rtt=mt')
inkam.add(kampus1, kampus2, kampus3, kampus4, kampus5)

@dp.message_handler(commands='test')
async def test_command(message: types.Message):
	await message.answer('По какому адресу Вы сейчас находитесь?', reply_markup=inkam)

#просто здравствуй просто как дела
@dp.message_handler()
async def echo_send(message : types.Message):
	if message.text == 'Привет':
		await message.answer('И тебе привет!')

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)