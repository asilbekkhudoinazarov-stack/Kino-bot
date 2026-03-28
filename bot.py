import logging
import json
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# ===== BOT TOKEN VA KANAL =====
API_TOKEN = os.getenv("BOT_TOKEN")  # Secrets dan olasiz
KANAL_ID = "@kino_top_24"            # Kanal username (masalan: @kino_top_24)
ADMINS = [7310599180, 5977950655]     # Admin Telegram ID lar

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)
DB_FILE = "movies.json"

# ===== BAZA FUNKSIYALARI =====
def load_movies():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_movies(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ===== OBUNA TEKSHIRISH =====
async def check_sub(user_id):
    try:
        member = await bot.get_chat_member(KANAL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ===== START =====
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if not await check_sub(message.from_user.id):
        btn = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=f"https://t.me/{KANAL_ID[1:]}")
        )
        return await message.answer("❌ Avval kanalga obuna bo‘ling!", reply_markup=btn)

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🎬 Kino kod yuborish"))
    kb.add(KeyboardButton("🆘 Yordam"))
    if message.from_user.id in ADMINS:
        kb.add(KeyboardButton("⚙️ Admin panel"))

    await message.answer("👋 Assalomu alaykum!\n🎬 Bu bot orqali siz kinoni topishingiz mumkin.\n🔑 Kino kodini yuboring!", reply_markup=kb)

# ===== HELP =====
@dp.message_handler(lambda m: m.text == "🆘 Yordam")
async def help_cmd(message: types.Message):
    await message.answer("📩 Yordam uchun admin bilan bog‘laning.")

# ===== ADMIN PANEL =====
@dp.message_handler(lambda m: m.text == "⚙️ Admin panel")
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ Kino qo‘shish")
    kb.add("📋 Kinolar ro‘yxati")
    kb.add("🗑 Kinoni o‘chirish")
    kb.add("📊 Bot statistikasini ko‘rish")
    kb.add("↩️ Ortga qaytish")
    await message.answer("⚙️ Admin panel", reply_markup=kb)

# ===== KINO QO‘SHISH =====
@dp.message_handler(lambda m: m.text == "➕ Kino qo‘shish")
async def add_movie(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    await message.answer("📤 Videoni yuboring")

    @dp.message_handler(content_types=types.ContentType.VIDEO)
    async def get_video(msg: types.Message):
        if msg.from_user.id not in ADMINS:
            return
        file_id = msg.video.file_id
        await msg.answer("🔑 Kino kodi yozing")

        @dp.message_handler()
        async def save_code(m):
            if m.from_user.id not in ADMINS:
                return
            code = m.text.strip()
            movies = load_movies()
            movies[code] = file_id
            save_movies(movies)
            await m.answer(f"✅ Kino saqlandi!\nKod: {code}")
            dp.message_handlers.unregister(save_code)

# ===== KINOLAR RO‘YXATI =====
@dp.message_handler(lambda m: m.text == "📋 Kinolar ro‘yxati")
async def movies_list(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    movies = load_movies()
    if not movies:
        await message.answer("❌ Bazada kino mavjud emas.")
    else:
        text = "🎬 Bazadagi kinolar:\n"
        for code in movies:
            text += f"🔑 {code}\n"
        await message.answer(text)

# ===== KINONI O‘CHIRISH =====
@dp.message_handler(lambda m: m.text == "🗑 Kinoni o‘chirish")
async def delete_movie(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    await message.answer("🔑 O‘chirmoqchi bo‘lgan kino kodini yuboring")

    @dp.message_handler()
    async def remove_code(m):
        if m.from_user.id not in ADMINS:
            return
        code = m.text.strip()
        movies = load_movies()
        if code in movies:
            movies.pop(code)
            save_movies(movies)
            await message.answer(f"✅ Kino {code} o‘chirildi")
        else:
            await message.answer("❌ Bunday kino topilmadi")
        dp.message_handlers.unregister(remove_code)

# ===== BOT STATISTIKASI =====
@dp.message_handler(lambda m: m.text == "📊 Bot statistikasini ko‘rish")
async def bot_stats(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    movies = load_movies()
    await message.answer(f"🎬 Bazadagi kinolar soni: {len(movies)} ta")

# ===== ORTGA QAYTISH =====
@dp.message_handler(lambda m: m.text == "↩️ Ortga qaytish")
async def back_admin(message: types.Message):
    await admin_panel(message)

# ===== KINO BERISH =====
@dp.message_handler()
async def send_movie(message: types.Message):
    if not await check_sub(message.from_user.id):
        btn = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=f"https://t.me/{KANAL_ID[1:]}")
        )
        return await message.answer("❌ Kanalga obuna bo‘ling!", reply_markup=btn)

    code = message.text.strip()
    movies = load_movies()
    if code in movies:
        await bot.send_video(message.chat.id, movies[code])
    else:
        await message.answer("❌ Bunday kino topilmadi!")

# ===== FLASK SERVER (PING UCHUN) =====
app = Flask("")

@app.route("/")
def home():
    return "Bot ishlayapti ✅"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    from threading import Thread
    t = Thread(target=run)
    t.start()

# ===== BOTNI ISHGA TUSHURISH =====
if __name__ == "__main__":
    keep_alive()
    executor.start_polling(dp, skip_updates=True)