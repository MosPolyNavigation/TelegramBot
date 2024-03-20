import asyncio
import logging
from datetime import datetime

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy

from env import *
from handlers import basic_router


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
    dp.include_router(basic_router)

    poll_waiting = asyncio.create_task(send_poll())
    poll_waiting

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


# отправка опроса в определенный день и время
async def send_poll():
    # день, месяц, год и время отправки опроса
    scheduled_time = datetime(2024, 3, 23, 18, 0, 0)

    # ожидание до момента отправки опроса
    while datetime.now() < scheduled_time:
        await asyncio.sleep(60)  # проверка каждую минуту

    # получение списка пользователей, которые воспользовались командой старт в заданный период
    start_time = '2024-03-01 00:00:00'
    end_time = '2024-03-21 23:59:59'
    users = await get_users_in_period(start_time, end_time)

    # отправка опроса каждому пользователю из списка
    for user_id in users:
            if user_id in voted_users: continue
            await bot.send_poll(chat_id = user_id,
                                    question = 'День открытых дверей окончен.\nПожалуйста, оцените работу бота', 
                                    options = ['Отлично',
                                         'Хорошо',
                                         'Удовлетворительно', 
                                         'Плохо',
                                         'Ужасно'],
                                    is_anonymous = False,
                                    type = 'regular',
                                    allows_multiple_answers = False)


# Функция для получения списка пользователей, воспользовавшихся командой старт в заданный период
async def get_users_in_period(start_time, end_time):
    cursor.execute('SELECT DISTINCT user_id FROM user_stat WHERE timestamp BETWEEN ? AND ?', (start_time, end_time))
    users = [row[0] for row in cursor.fetchall()]
    return users

# Запуск бота

if __name__ == "__main__":
    asyncio.run(main())
