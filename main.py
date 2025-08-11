from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Стан машини (FSM)
class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()

# Кнопка купити — запит ПІБ
@dp.message(F.text == "🛒 Купити")
async def buy_product(message: types.Message, state: FSMContext):
    await message.answer("Введіть, будь ласка, ваше ПІБ:")
    await state.set_state(OrderStates.waiting_for_name)

# Обробка введення ПІБ
@dp.message(OrderStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    full_name = message.text.strip()
    await state.update_data(full_name=full_name)

    # Запит номера телефону
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Надіслати номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Дякуємо! Тепер натисніть кнопку нижче, щоб поділитися своїм номером телефону:", reply_markup=kb)
    await state.set_state(OrderStates.waiting_for_phone)

# Обробка номера
@dp.message(F.contact, OrderStates.waiting_for_phone)
async def contact_handler(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    data = await state.get_data()
    full_name = data.get("full_name")

    await message.answer(
        f"✅ Дякуємо, {full_name}!\n"
        f"Ваше замовлення на {product_name} прийняте.\n"
        f"Ми зв'яжемося з вами за номером {phone}.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

