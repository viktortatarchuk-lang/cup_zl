import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Завантажуємо токен з .env
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

# Ініціалізація бота та диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

# Визначення станів
class Form(StatesGroup):
    waiting_for_name = State()

# /start команда
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Введіть своє ПІБ:")

# Обробка введення ПІБ
@dp.message(Form.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    user_name = message.text.strip()
    await state.update_data(name=user_name)
    await message.answer(f"Дякую, {user_name}, за відповідь!")
    await state.clear()

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
