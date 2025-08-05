import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiohttp import web
from dotenv import load_dotenv

# Завантаження .env
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

WEBHOOK_HOST = 'https://cup-zl.onrender.com'
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Інформація про товар
product_name = "Футболка 'Донт пуш зе хорсес!'"
product_price = 500
product_description = "Крута футболка з унікальним принтом."
product_photo_url = "https://images.prom.ua/6058088044_w640_h640_6058088044.jpg"

# /start
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

# Кнопка купити
@dp.message(F.text == "🛒 Купити")
async def buy_product(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Надіслати номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Натисніть кнопку нижче, щоб поділитися своїм номером телефону:", reply_markup=kb)

# Отримання контакту
@dp.message(F.contact)
async def contact_handler(message: types.Message):
    phone = message.contact.phone_number
    await message.answer(
        f"✅ Дякуємо! Ваше замовлення на {product_name} прийняте.\n"
        f"Ми зв'яжемося з вами за номером {phone}.",
        reply_markup=ReplyKeyboardRemove()
    )

# Webhook
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
