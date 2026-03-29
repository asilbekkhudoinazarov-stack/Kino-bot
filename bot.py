import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

from db import add_movie, get_movie, delete_movie, get_all_movies

API_TOKEN = os.getenv("BOT_TOKEN")
KANAL_ID = "@kino_top_24"
ADMINS = [5977950655, 7310599180]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

# ===== OBUNA =====
async def check_sub(user_id):
    try:
        member = await bot.get_chat_member(chat_id=KANAL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ===== MENULAR =====
def main_menu(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🎬 Kino kod yuborish")
    kb.add("🆘 Yordam")
    if user_id in ADMINS:
        kb.add("⚙️ Admin panel")
    return kb

def admin_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ Kino qo‘shish")
    kb.add("📋 Kinolar ro‘yxati")
    kb.add("🗑 Kinoni o‘chirish")
    kb.add("📊 Statistika")
    kb.add("↩️ Ortga qaytish")
    return kb

# ===== START =====
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if not await check_sub(message.from_user.id):
        btn = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📢 Obuna bo‘lish", url=f"https://t.me/{KANAL_ID[1:]}")
        )
        return await message.answer("❌ Avval kanalga obuna bo‘ling!", reply_markup=btn)

    await message.answer("👋 Xush kelibsiz!\n🔑 Kino kodini yuboring.", reply_markup=main_menu(message.from_user.id))

# ===== KOD SO‘RASH =====
@dp.message_handler(lambda m: m.text == "🎬 Kino kod yuborish")
async def ask_code(message: types.Message):
    await message.answer("🔑 Kino kodini yozing:")

# ===== HELP =====
@dp.message_handler(lambda m: m.text == "🆘 Yordam")
async def help_cmd(message: types.Message):
    await message.answer("📩 Admin bilan bog‘laning.")

# ===== ADMIN PANEL =====
@dp.message_handler(lambda m: m.text == "⚙️ Admin panel")
async def admin_panel(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer("⚙️ Admin panel", reply_markup=admin_menu())

# ===== ORTGA =====
@dp.message_handler(lambda m: m.text == "↩️ Ortga qaytish")
async def back(message: types.Message):
    await message.answer("🏠 Bosh menyu", reply_markup=main_menu(message.from_user.id))

# ===== KINO QO‘SHISH =====
@dp.message_handler(lambda m: m.text == "➕ Kino qo‘shish")
async def add_movie_handler(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    await message.answer("📤 Video yuboring")

    @dp.message_handler(content_types=types.ContentType.VIDEO)
    async def get_video(msg: types.Message):
        file_id = msg.video.file_id
        await msg.answer("🔑 Kod yozing")

        @dp.message_handler()
        async def save_code(m):
            code = m.text.strip()
            add_movie(code, file_id)
            await m.answer("✅ Saqlandi!")
            dp.message_handlers.unregister(save_code)

# ===== RO‘YXAT =====
@dp.message_handler(lambda m: m.text == "📋 Kinolar ro‘yxati")
async def list_movies(message: types.Message):
    movies = get_all_movies()
    if not movies:
        await message.answer("❌ Bo‘sh")
    else:
        await message.answer("\n".join(movies))

# ===== O‘CHIRISH =====
@dp.message_handler(lambda m: m.text == "🗑 Kinoni o‘chirish")
async def delete_handler(message: types.Message):
    await message.answer("🔑 Kod yozing")

    @dp.message_handler()
    async def remove(m):
        delete_movie(m.text.strip())
        await m.answer("✅ O‘chirildi")
        dp.message_handlers.unregister(remove)

# ===== STATISTIKA =====
@dp.message_handler(lambda m: m.text == "📊 Statistika")
async def stats(message: types.Message):
    movies = get_all_movies()
    await message.answer(f"🎬 Kinolar soni: {len(movies)}")

# ===== KINO BERISH =====
@dp.message_handler()
async def send_movie(message: types.Message):
    if not await check_sub(message.from_user.id):
        btn = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📢 Obuna bo‘lish", url=f"https://t.me/{KANAL_ID[1:]}")
        )
        return await message.answer("❌ Obuna bo‘ling!", reply_markup=btn)

    file_id = get_movie(message.text.strip())

    if file_id:
        await bot.send_video(message.chat.id, file_id)
    else:
        await message.answer("❌ Topilmadi")

# ===== FLASK =====
app = Flask("")

@app.route("/")
def home():
    return "Bot ishlayapti"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run).start()

# ===== RUN =====
if __name__ == "__main__":
    keep_alive()
    executor.start_polling(dp, skip_updates=True)