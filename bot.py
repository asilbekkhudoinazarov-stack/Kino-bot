import logging
import json
import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv("8735477684:AAE0vS34otIUJFHehfqCWslivG-j_vFK7gc")
KANAL_ID = "@kino_top_24"
ADMINS = [7310599180, 5977950655]

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

DB_FILE = "movies.json"

def load_movies():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_movies(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

async def check_sub(user_id):
    try:
        member = await bot.get_chat_member(KANAL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

user_state = {}
user_data = {}
STATE_WAIT_VIDEO = "wait_video"
STATE_WAIT_CODE = "wait_code"

@dp.message(Command("start"))
async def start(message: types.Message):
    if not await check_sub(message.from_user.id):
        btn = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=f"https://t.me/{KANAL_ID[1:]}")
        ]])
        return await message.answer("❌ Avval kanalga obuna bo'ling!", reply_markup=btn)
    kb_buttons = [[KeyboardButton(text="🎬 Kino kod yuborish")], [KeyboardButton(text="🆘 Yordam")]]
    if message.from_user.id in ADMINS:
        kb_buttons.append([KeyboardButton(text="⚙️ Admin panel")])
    kb = ReplyKeyboardMarkup(keyboard=kb_buttons, resize_keyboard=True)
    await message.answer("👋 Assalomu alaykum!\n\n🎬 Bu bot orqali siz istalgan kinoni topishingiz mumkin.\n🔑 Kino kodini yuboring!", reply_markup=kb)

@dp.message(F.text == "🆘 Yordam")
async def help_cmd(message: types.Message):
    await message.answer("📩 Yordam uchun admin bilan bog'laning.")

@dp.message(F.text == "⚙️ Admin panel")
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="➕ Kino qo'shish")], [KeyboardButton(text="📊 Statistika")]], resize_keyboard=True)
    await message.answer("⚙️ Admin panel", reply_markup=kb)

@dp.message(F.text == "➕ Kino qo'shish")
async def add_movie_start(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    user_state[message.from_user.id] = STATE_WAIT_VIDEO
    await message.answer("📤 Videoni yuboring")

@dp.message(F.text == "📊 Statistika")
async def stats(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    movies = load_movies()
    await message.answer(f"🎬 Bazadagi kinolar soni: {len(movies)} ta")

@dp.message(F.video)
async def get_video(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    if user_state.get(message.from_user.id) != STATE_WAIT_VIDEO:
        return
    user_data[message.from_user.id] = {"file_id": message.video.file_id}
    user_state[message.from_user.id] = STATE_WAIT_CODE
    await message.answer("🔑 Kino kodi yozing")

@dp.message()
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    if user_state.get(user_id) == STATE_WAIT_CODE and user_id in ADMINS:
        code = message.text.strip()
        file_id = user_data.get(user_id, {}).get("file_id")
        if file_id:
            movies = load_movies()
            movies[code] = file_id
            save_movies(movies)
            await message.answer(f"✅ Kino saqlandi!\nKod: {code}")
        user_state.pop(user_id, None)
        user_data.pop(user_id, None)
        return
    if not await check_sub(user_id):
        btn = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=f"https://t.me/{KANAL_ID[1:]}")
        ]])
        return await message.answer("❌ Kanalga obuna bo'ling!", reply_markup=btn)
    code = message.text.strip()
    movies = load_movies()
    if code in movies:
        await bot.send_video(message.chat.id, movies[code])
    else:
        await message.answer("❌ Bunday kino topilmadi!")

async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())