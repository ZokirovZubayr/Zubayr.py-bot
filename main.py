import logging
import sqlite3

from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from default_keyboard import menu
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# LOG
logging.basicConfig(level=logging.INFO)

# BOT
bot = Bot(token="8123690584:AAFXoPb6w-bBZbeOsdzsAXEApL1QHU25a0E")
dp = Dispatcher(bot, storage=MemoryStorage())

# === DATABASE FUNCTIONS ===
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # oldingi users jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER,
            name TEXT,
            surname TEXT,
            age TEXT,
            phone TEXT
        )
    """)
    # yangi messages jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER,
            text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def insert_user(tg_id, name, surname, age, phone):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (tg_id, name, surname, age, phone) VALUES (?, ?, ?, ?, ?)",
        (tg_id, name, surname, age, phone)
    )
    conn.commit()
    conn.close()

def insert_message(tg_id, text):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (tg_id, text) VALUES (?, ?)",
        (tg_id, text)
    )
    conn.commit()
    conn.close()

# === STATES ===
class Form(StatesGroup):
    name = State()
    surname = State()
    age = State()
    phone = State()

class MessageForm(StatesGroup):
    text = State()

# === START & REGISTRATION HANDLERS ===
@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await Form.name.set()
    await message.answer("Ismingizni kiriting:", reply_markup=ReplyKeyboardRemove())

@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await Form.next()
    await message.answer("Familiyangizni kiriting:")

@dp.message_handler(state=Form.surname)
async def process_surname(message: types.Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await Form.next()
    await message.answer("Yoshingizni kiriting:")

@dp.message_handler(state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await Form.next()

    contact_button = KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(contact_button)
    await message.answer("Telefon raqamingizni tugma orqali yuboring:", reply_markup=keyboard)

@dp.message_handler(content_types=types.ContentType.CONTACT, state=Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    # saqlash
    await state.update_data(phone=message.contact.phone_number)
    data = await state.get_data()
    insert_user(
        tg_id=message.from_user.id,
        name=data['name'],
        surname=data['surname'],
        age=data['age'],
        phone=data['phone']
    )

    # xabar va menu chiqarish
    await message.answer("✅ Ma'lumotlaringiz saqlandi!", reply_markup=ReplyKeyboardRemove())
    summary = (
        f"Ism: {data['name']}\n"
        f"Familiya: {data['surname']}\n"
        f"Yosh: {data['age']}\n"
        f"Telefon: {data['phone']}"
    )
    await message.answer(summary, reply_markup=menu)
    await state.finish()

# === MAIN MENU HANDLERS ===
@dp.message_handler(Text(equals="Kanal haqida 🏢"), state=None)
async def about_channel(message: types.Message):
    await message.answer(
        "Zubayr.py kanalida siz kodlar, veb saytlar, Telegram botlar va yangiliklardan xabardor bo‘lasiz. "
        "Python va boshqa dasturlash tillari haqida malumotlar boladi!"
    )

@dp.message_handler(Text(equals="Admin bilan bog'lanish 🥷"), state=None)
async def about_admins(message: types.Message):
    await message.answer("Adminlar:\n\n1. @Zubayr_Zokirov\n2. @Zubayr712")



@dp.message_handler(Text(equals="📎 Foydali linklar"), state=None)
async def useful_links(message: types.Message):
    await message.answer(
        "Foydali linklar:\n"
        "1. https://www.w3schools.com/ — barcha dasturlash tillarini o'rganishingiz mumkin\n"
        "2. https://github.com/ — kodlarni saqlash\n"
        "3. https://free-css.com/ — tayor sayt uchun kodlar\n"
        "4. https://getbootstrap.com/ — tayyor kodlar\n"
    )

# === “📨 Habar qoldirish” ===
# — menu’ga yangi tugma qo‘shamiz:
menu.add(KeyboardButton("📨 Habar qoldirish"))

@dp.message_handler(Text(equals="📨 Habar qoldirish"), state=None)
async def ask_message(message: types.Message):
    await MessageForm.text.set()
    await message.answer("📨 Siz bu yerda adminga habar qoldirishingiz mumkin!")

@dp.message_handler(state=MessageForm.text, content_types=types.ContentTypes.TEXT)
async def process_message(message: types.Message, state: FSMContext):
    insert_message(tg_id=message.from_user.id, text=message.text)
    await message.answer("✅ Xabaringiz saqlandi! Tez orada javob beramiz.", reply_markup=menu)
    await state.finish()

@dp.message_handler(commands="help")
async def cmd_help(message: types.Message):
    await message.answer("Siz bu botda kanal haqida malumot olishingiz mumkin, foydali linklar va admin bilan bog'lanishingiz mumkin.\n\n")

# === RUN ===
if __name__ == "__main__":
    init_db()
    executor.start_polling(dp, skip_updates=True)

