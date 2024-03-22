import asyncio
import logging
from datetime import datetime, time

from asgiref.sync import async_to_sync
import pytz
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram import types

from env import *
from handlers import basic_router


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
    dp.include_router(basic_router)

    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(dp.start_polling(bot, handle_as_tasks=True, allowed_updates=dp.resolve_used_update_types()))
    while True:
        asyncio.create_task(send_dod())
        await asyncio.sleep(60)


# отправка программы ДОД

async def send_dod():
    # год, месяц, день, время отправки файла и ограничение
    scheduled_time_1 = datetime(2024, 3, 23, 9, 0, 0)
    scheduled_time_2 = datetime(2024, 3, 23, 9, 1, 0)

    # ожидание до момента отправки файла
    while datetime.now() < scheduled_time_1 or datetime.now() > scheduled_time_2:
        return 0
    # получение списка всех пользователей
    users = await get_all_users()

    file_pdf = 'Программа Дня открытых дверей.pdf'
    file = types.FSInputFile(file_pdf)
    for user_id in users:
        await bot.send_document(chat_id=user_id,
                                caption="Привет 🕊\n\nСегодня в проходит день открытых дверей. Забирай программу мероприятий, чтобы не пропустить ничего интересного, а также используй команду /restart для обновления бота и просмотра новых функций. \n\nВстречаемся в 11:00 на Большой Семеновской, 38",
                                document=file)
    return 0


# отправка опроса в определенный день и время
async def send_poll():
    # день, месяц, год и время отправки опроса
    scheduled_time = datetime(2024, 2, 10, 18, 0, 0)

    # ожидание до момента отправки опроса
    while datetime.now() < scheduled_time:
        await asyncio.sleep(60)  # проверка каждую минуту

    # получение списка пользователей, которые воспользовались командой старт в заданный период
    start_time = '2024-02-01 00:00:00'
    end_time = '2024-02-12 23:59:59'
    users = await get_users_in_period(start_time, end_time)

    # отправка опроса каждому пользователю из списка
    for user_id in users:
        poll_message = await bot.send_poll(chat_id=user_id,
                                           question='День открытых дверей окончен.\nОцените пожалуйста работу бота.',
                                           options=['1', '2', '3', '4', '5'])

        # запись результатов опроса
        await asyncio.sleep(14400)
        poll_result = await bot.stop_poll(chat_id=user_id, message_id=poll_message.message_id)
        poll_results[user_id] = poll_result


# Функция для получения списка пользователей, воспользовавшихся командой старт в заданный период
async def get_users_in_period(start_time, end_time):
    cursor.execute('SELECT DISTINCT user_id FROM user_stat WHERE timestamp BETWEEN ? AND ?', (start_time, end_time))
    users = [row[0] for row in cursor.fetchall()]
    return users('SELECT DISTINCT user_id FROM user_stat')


async def get_all_users():
    cursor.execute('SELECT DISTINCT user_id FROM user_stat')
    users = [row[0] for row in cursor.fetchall()]
    return users


async def scheduler():
    while True:
        try:
            await send_poll()
        except Exception as e:
            print(f'An error occurred: {e}')
        finally:
            await asyncio.sleep(86400)  # повтор проверки каждые 24 часа (86400 секунды)


# asyncio.get_running_loop().create_task(send_dod())
# Запуск бота

if __name__ == "__main__":
    asyncio.run(main())
