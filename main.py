import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

WEBHOOK_HOST = 'https://cup-zl.onrender.com'
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())  # Підключаємо FSM storage

logging.basicConfig(level=logging.INFO)

product_name = "Футболка 'Донт пуш зе хорсес!'"
product_price = 500
product_description = "Крута футболка з унікальним принтом."
product_photo_url = "https://images.prom.ua/6058088044_w640_h640_6058088044.jpg"

# Визначення станів
class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🛒 Купити")]],
        resize_keyboard=True
    )
    await message.answer_photo(
        photo=product_photo_url,
        caption=f"{product_name}\n\n{product_description}\nЦіна: {product_price} грн",
        reply_markup=kb
    )

@dp.message(F.text == "🛒 Купити")
async def buy_product(message: types.Message, state: FSMContext):
    await state.set_state(OrderStates.waiting_for_name)
    await message.answer("Будь ласка, введіть своє ПІБ:", reply_markup=ReplyKeyboardRemove())

@dp.message(OrderStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    full_name = message.text.strip()
    await state.update_data(full_name=full_name)

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Надіслати номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await state.set_state(OrderStates.waiting_for_phone)
    await message.answer("Дякую! Тепер натисніть кнопку, щоб надіслати свій номер телефону:", reply_markup=kb)

@dp.message(OrderStates.waiting_for_phone, F.contact)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    full_name = data.get("full_name")
    phone = message.contact.phone_number

    await message.answer(
        f"✅ Дякуємо, **{full_name}**!\n"
        f"Ваше замовлення на {product_name} прийняте.\n"
        f"Ми зв'яжемося з вами за номером {phone}.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

# Webhook logic
async def on_startup(app): await bot.set_webhook(WEBHOOK_URL)
async def on_shutdown(app): await bot.delete_webhook()
async def handle_webhook(request):
    update = await request.json()
    await dp.feed_update(bot, types.Update(**update))
    return web.Response()

def create_app():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

if __name__ == '__main__':
    web.run_app(create_app(), port=int(os.getenv("PORT", 8000)))
