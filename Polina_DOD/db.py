from env import *

# создание необхимых таблиц в базе данных
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

cursor.execute('''CREATE TABLE IF NOT EXISTS file_stats (
                    user_id INTEGER,
                    timestamp TEXT
                )''')


# функции для подсчета общего количества пользователей за определенный период времени (за весь период, декабрь, январь и тд)
async def count_users_stat(start_time, end_time):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_stat WHERE timestamp BETWEEN ? AND ?',
                   (start_time, end_time))
    total_users = cursor.fetchone()[0]
    return total_users


async def count_users_month(start_time, end_time):
    cursor.execute(
        'SELECT COUNT(DISTINCT user_id) FROM user_stat WHERE timestamp BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM user_stat WHERE timestamp < ?)',
        (start_time, end_time, start_time))
    users_month = cursor.fetchone()[0]
    return users_month


# функции для подсчета общего количества пользователей за выбранный период времени (за весь период, декабрь, январь и тд)
async def count_users_url(start_url, end_url):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM url WHERE timestampurl BETWEEN ? AND ?', (start_url, end_url))
    total_url = cursor.fetchone()[0]
    return total_url


async def count_users_month_url(start_url, end_url):
    cursor.execute(
        'SELECT COUNT(DISTINCT user_id) FROM url WHERE timestampurl BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM url WHERE timestampurl < ?)',
        (start_url, end_url, start_url))
    users_month_url = cursor.fetchone()[0]
    return users_month_url


async def count_users_file(start_time, end_time):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM file_stats WHERE timestamp BETWEEN ? AND ?',
                   (start_time, end_time))
    total_users = cursor.fetchone()[0]
    return total_users


async def count_users_month_file(start_time, end_time):
    cursor.execute(
        'SELECT COUNT(DISTINCT user_id) FROM file_stats WHERE timestamp BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM file_stats WHERE timestamp < ?)',
        (start_time, end_time, start_time))
    users_month = cursor.fetchone()[0]
    return users_month
