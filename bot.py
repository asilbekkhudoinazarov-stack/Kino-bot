import logging
import json
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ===== TOKEN VA KANAL =====
API_TOKEN = os.getenv 8735477684:AAE0vS34otIUJFHehfqCWslivG-j_vFK7gc # tokenni Railway Variablesga qo'y
KANAL_ID = @kino_top_24  # kanal username

# ===== ADMINLAR =====
ADMINS = [7310599180, 5977950655]  # SEN VA DOSTING ID

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

    # USER MENU
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🎬 Kino kod yuborish"))
    kb.add(KeyboardButton("🆘 Yordam"))

    # ADMIN PANEL FAOL
    if message.from_user.id in ADMINS:
        kb.add(KeyboardButton("⚙️ Admin panel"))

    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "🎬 Bu bot orqali siz istalgan kinoni topishingiz mumkin.\n"
        "🔑 Kino kodini yuboring!",
        reply_markup=kb
    )

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
    kb.add("📊 Statistika")
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
        await msg.answer("🔑 Kod yozing")

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

# ===== STATISTIKA =====
@dp.message_handler(lambda m: m.text == "📊 Statistika")
async def stats(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    movies = load_movies()
    await message.answer(f"🎬 Bazadagi kinolar soni: {len(movies)} ta")

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

# ===== BOTNI ISHGA TUSHURISH =====
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
