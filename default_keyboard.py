from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

menu = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="Kanal haqida 🏢"), KeyboardButton("📎 Foydali linklar"),
        KeyboardButton(text="Admin bilan bog'lanish 🥷")
    ]
],resize_keyboard=True)