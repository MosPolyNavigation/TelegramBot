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

cursor.execute("PRAGMA table_info(url)")
columns = cursor.fetchall()

timestampurl_exists = False
for column in columns:
    if column[1] == 'timestampurl':
        timestampurl_exists = True
        break

# если в таблице url есть столбец timestampurl, переименовываем его на timestamp (это нужно для использования функции по подсчёту пользователей, не вмешиваясь в бд)
if timestampurl_exists:
    cursor.execute("ALTER TABLE url RENAME COLUMN timestampurl TO timestamp")

cursor.execute('''CREATE TABLE IF NOT EXISTS user_votes (
                    user_id INTEGER,
                    answer TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS file_stats (
                    user_id INTEGER,
                    timestamp TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS network_stats (
                    user_id INTEGER,
                    timestamp TEXT
                )''')

#функция для подсчета общего количества пользователей, нажавших на каждую кнопку соответственно, за весь период
async def count_users_button(table_name, start_time, end_time):
    cursor.execute(f'SELECT COUNT(DISTINCT user_id) FROM {table_name} WHERE timestamp BETWEEN ? AND ?', (start_time, end_time))
    total_users = cursor.fetchone()[0] #новые (уникальные) пользователи
    cursor.execute(f'SELECT COUNT(*) FROM {table_name} WHERE timestamp BETWEEN ? AND ?', (start_time, end_time))
    total_clicks = cursor.fetchone()[0] #все нажатия на кнопку
    return total_users, total_clicks
  
#функция для подсчета количества пользователей, нажавших на каждую кнопку соответственно, помесячно
async def count_users_month(table_name, start_time, end_time):
    cursor.execute(
        f'SELECT COUNT(DISTINCT user_id) FROM {table_name} WHERE timestamp BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM {table_name} WHERE timestamp < ?)',
        (start_time, end_time, start_time))
    users_month = cursor.fetchone()[0] #новые (уникальные) пользователи
    cursor.execute(f'SELECT COUNT(*) FROM {table_name} WHERE timestamp BETWEEN ? AND ?', (start_time, end_time))
    total_month = cursor.fetchone()[0] #все нажатия на кнопку
    return users_month, total_month
