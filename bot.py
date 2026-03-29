from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from db import add_movie, get_movie, delete_movie
import os

TOKEN = "SENING_BOT_TOKENING"  # <-- bu yerga o'zingning tokeningni qo'y
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Adminlar ro'yxati
ADMINS = [7310599180, 5977950655]  # <-- bu yerga admin telegram idlarini qo'y

# Boshlang'ich tugmalar
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("➕ Kino qo‘shish"))
main_kb.add(KeyboardButton("📽 Kinoni ko‘rish"))

# State saqlash (qaysi admin video tashlamoqchi)
admin_state = {}

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Salom! Botga xush kelibsiz.", reply_markup=main_kb)

# Admin kino qo‘shish tugmasini bosganda
@dp.message_handler(lambda m: m.text == "➕ Kino qo‘shish" and m.from_user.id in ADMINS)
async def add_movie_start(message: types.Message):
    admin_state[message.from_user.id] = "await_video"
    await message.answer("Videoni yuboring:")

# Video kelganda
@dp.message_handler(content_types=["video"])
async def handle_video(message: types.Message):
    user_id = message.from_user.id
    if admin_state.get(user_id) == "await_video":
        file_id = message.video.file_id
        admin_state[user_id] = "await_code"
        admin_state[f"{user_id}_file_id"] = file_id
        await message.answer("Kodini yozing:")
    else:
        await message.answer("❌ Ruxsat yo‘q yoki noto‘g‘ri holat.")

# Kod yozilganda
@dp.message_handler(lambda m: True)
async def handle_code(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Agar admin video yuborgan bo‘lsa
    if admin_state.get(user_id) == "await_code":
        file_id = admin_state.get(f"{user_id}_file_id")
        add_movie(text, file_id)
        admin_state.pop(user_id)
        admin_state.pop(f"{user_id}_file_id")
        await message.answer(f"✅ Kino qo‘shildi! Kod: {text}")
        return

    # Agar foydalanuvchi kod bilan kinoni ko‘rmoqchi bo‘lsa
    file_id = get_movie(text)
    if file_id:
        await bot.send_video(message.chat.id, file_id)
    else:
        await message.answer("❌ Kino topilmadi.")
        
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)