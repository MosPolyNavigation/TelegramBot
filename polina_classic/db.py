from env import *

#создание необхимых таблиц в базе данных
cursor.execute('''CREATE TABLE IF NOT EXISTS user_stat (
                    user_id INTEGER,
                    timestamp TEXT
                )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS url (
                    user_id INTEGER,
                    timestampurl TEXT
                )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS user_votes (
                    user_id INTEGER,
                    answer TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS classic_users (
                    user_id INTEGER,
                    timestamp TEXT
                )''')

#функции для подсчета общего количества пользователей за определенный период времени (за весь период, декабрь, январь и тд)
async def count_users_stat(start_time, end_time):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM classic_users WHERE timestamp BETWEEN ? AND ?', (start_time, end_time))
    total_users = cursor.fetchone()[0]
    return total_users

async def count_users_month(start_time, end_time):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM classic_users WHERE timestamp BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM classic_users WHERE timestamp < ?)',
                   (start_time, end_time, start_time))
    users_month = cursor.fetchone()[0]
    return users_month


