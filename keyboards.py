from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Foydalanuvchi tugmalari
start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(KeyboardButton("Kino kodi yuborish"))

# Admin tugmalari
admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_kb.add(KeyboardButton("Kino qo'shish"))
admin_kb.add(KeyboardButton("Kino o'chirish"))
admin_kb.add(KeyboardButton("Statistika"))