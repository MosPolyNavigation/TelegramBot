from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from env import *

events_kb = InlineKeyboardMarkup(inline_keyboard=[], resize_keyboard = True)

for i in inline_kbs['events']:
    events_kb.inline_keyboard.append([InlineKeyboardButton(text=i['header'], callback_data=f"generic_{i['key']}")])

# Стандартная клавиатура
startkb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Новый маршрут 📌')],
    [KeyboardButton(text='Библиотека карт 🗺')],
    [KeyboardButton(text='Наши соцсети ✉')],
    [KeyboardButton(text='Программа ДОД 📄')]
], resize_keyboard=True)

emptyfieldkb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='-')]
], resize_keyboard=True)

builder = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="VK", url="https://vk.com/mospolynavigation")],
    [InlineKeyboardButton(text="Telegram", url="https://t.me/mospolynavigation")]
], resize_keyboard=True)

cancel_menu = InlineKeyboardMarkup(inline_keyboard = [
    [InlineKeyboardButton(text = "❌ Отменить дейстие", callback_data = "cancel_action")]
], resize_keyboard = True)

# Загрузка данных из JSON-файла
def load_data():
    with open('kb.json', 'r', encoding='utf-8-sig') as f:
        return json.load(f)

# Сохранение данных в JSON-файл
def save_data(data):
    with open('kb.json', 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def find_button_by_key(data, key):
    # Проверяем, содержит ли текущий словарь (или его элементы) нужный ключ
    if isinstance(data, dict):
        if "key" in data and data["key"] == key:
            return data
        # Если ключ не совпадает, но есть вложенные кнопки, ищем в них
        if "inner_kb" in data:
            return find_button_by_key(data["inner_kb"], key)
    # Если текущий элемент - это список, проверяем каждый его элемент
    elif isinstance(data, list):
        for item in data:
            result = find_button_by_key(item, key)
            if result:
                return result
    # Если кнопка не найдена, возвращаем None
    return None

def add_button(data, target_key, new_button):
    if isinstance(data, dict):
        if target_key == "root":
            data.update(new_button)
            return True
        if "key" in data and data["key"] == target_key:
            if "inner_kb" in data:
                data["inner_kb"].append(new_button)
                return True
            else:
                data["inner_kb"] = [new_button]
                return True
        if "inner_kb" in data:
            return add_button(data["inner_kb"], target_key, new_button)
    elif isinstance(data, list):
        for item in data:
            if add_button(item, target_key, new_button):
                return True
    return False

def delete_button(data, target_key):
    if isinstance(data, dict):
        if "key" in data and data["key"] == target_key:
            return True
        if "inner_kb" in data:
            data["inner_kb"] = [item for item in data["inner_kb"] if not delete_button(item, target_key)]
            return False  # Сохраняем родительский элемент
    elif isinstance(data, list):
        new_data = []
        for item in data:
            if not delete_button(item, target_key):
                new_data.append(item)
        data.clear()
        data.extend(new_data)
        return True
    return False