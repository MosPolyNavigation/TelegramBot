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

#функции для подсчета общего количества пользователей за определенный период времени (за весь период, декабрь, январь и тд)
async def count_users_stat(start_time, end_time):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_stat WHERE timestamp BETWEEN ? AND ?', (start_time, end_time))
    total_users = cursor.fetchone()[0]
    return total_users

async def count_users_December(start_December, end_December):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_stat WHERE timestamp BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM user_stat WHERE timestamp < ?)',
                   (start_December, end_December, start_December))
    users_December = cursor.fetchone()[0]
    return users_December

async def count_users_January(start_January, end_January):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_stat WHERE timestamp BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM user_stat WHERE timestamp < ?)',
                   (start_January, end_January, start_January))
    users_January = cursor.fetchone()[0]
    return users_January

async def count_users_February(start_February, end_February):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_stat WHERE timestamp BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM user_stat WHERE timestamp < ?)',
                   (start_February, end_February, start_February))
    users_February = cursor.fetchone()[0]
    return users_February


#функции для подсчета общего количества пользователей за выбранный период времени (за весь период, декабрь, январь и тд)
async def count_users_url(start_url, end_url):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM url WHERE timestampurl BETWEEN ? AND ?', (start_url, end_url))
    total_url = cursor.fetchone()[0]
    return total_url

async def count_users_url_December(start_url_December, end_url_December):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM url WHERE timestampurl BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM url WHERE timestampurl < ?)',
                   (start_url_December, end_url_December, start_url_December))
    users_url_December = cursor.fetchone()[0]
    return users_url_December

async def count_users_url_January(start_url_January, end_url_January):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM url WHERE timestampurl BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM url WHERE timestampurl < ?)',
                   (start_url_January, end_url_January, start_url_January))
    users_url_January = cursor.fetchone()[0]
    return users_url_January

async def count_users_url_February(start_url_February, end_url_February):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM url WHERE timestampurl BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM url WHERE timestampurl < ?)',
                   (start_url_February, end_url_February, start_url_February))
    users_url_February = cursor.fetchone()[0]
    return users_url_February