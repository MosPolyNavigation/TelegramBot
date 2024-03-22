from env import *
import json
import pandas as pd

conn = sqlite3.connect('my.db')
cursor = conn.cursor()

df = pd.read_excel('Маршруты.xlsx')

data = df.to_json('records.json', orient='records')
parsed_data = json.loads(data)

for item in parsed_data:
    cursor.execute('''SELECT * FROM Auditoriums WHERE room_number = ? AND infa = ?''',
                   (item['Наименование корпуса'] + item['Номер аудитории'], item['Маршрут']))
    existing_record = cursor.fetchone()

    if existing_record:
        continue
    else:
        cursor.execute('''INSERT INTO Auditoriums (room_number, infa)
                      VALUES (?, ?)''', (item['Наименование корпуса'] + item['Номер аудитории'], item['Маршрут']))

conn.commit()
conn.close()
