from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

storage = MemoryStorage()

class AddNewButtonForm(StatesGroup):
    reading_header = State()
    reading_message = State()
    reading_query = State()

class AddNewMenuButtonForm(StatesGroup):
    reading_header = State()
    reading_message = State()

class DeleteButtonForm(StatesGroup):
    deleting = State()