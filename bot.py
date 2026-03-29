import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# TOKEN ni o'zingizning bot tokeningiz bilan almashtiring
BOT_TOKEN = "8735477684:AAE0vS34otIUJFHehfqCWslivG-j_vFK7gc"

# Adminlar ID sini qo'shing
ADMIN_IDS = [7310599180, 5977950655]  # misol

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# SQLite bazasi
conn = sqlite3.connect("kino.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS kino (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    file_id TEXT
                )""")
conn.commit()

# Kino qo'shish jarayoni uchun user step
kino_step = {}

# Asosiy menyu
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Kino qo‘shish"))
    return markup

# Start handler
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer("Salom! Botga xush kelibsiz.", reply_markup=main_menu())

# Kino qo'shish boshlanishi
@dp.message_handler(lambda message: message.text == "Kino qo‘shish")
async def add_kino_start(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Siz admin emassiz!")
        return
    kino_step[message.from_user.id] = "awaiting_name"
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Ortga"))
    await message.answer("Kino nomini yozing:", reply_markup=markup)

# Kino nomi va video qabul qilish
@dp.message_handler(content_types=["text", "video"])
async def handle_kino(message: types.Message):
    user_id = message.from_user.id

    # Ortga tugmasi
    if message.text == "Ortga":
        await start_handler(message)
        if user_id in kino_step:
            kino_step.pop(user_id)
        return

    # Kino qo‘shish jarayoni
    if user_id in kino_step:
        step = kino_step[user_id]

        # 1️⃣ Nomni olish
        if step == "awaiting_name" and message.text:
            kino_step[user_id] = {"name": message.text, "step": "awaiting_file"}
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton("Ortga"))
            await message.answer("Endi video faylini yuboring (mp4 formatda):", reply_markup=markup)

        # 2️⃣ Video olish
        elif isinstance(step, dict) and step.get("step") == "awaiting_file":
            if not message.video:
                await message.answer("Iltimos, faqat video yuboring!")
                return
            name = step["name"]
            file_id = message.video.file_id
            cursor.execute("INSERT INTO kino (name, file_id) VALUES (?, ?)", (name, file_id))
            conn.commit()
            await message.answer(f"{name} kinoni qo‘shdingiz ✅", reply_markup=main_menu())
            kino_step.pop(user_id)

# Kino ro‘yxatini ko‘rsatish (misol)
@dp.message_handler(commands=['kino'])
async def list_kino(message: types.Message):
    cursor.execute("SELECT name FROM kino")
    kinolar = cursor.fetchall()
    if kinolar:
        msg = "\n".join([kino[0] for kino in kinolar])
        await message.answer(f"Mavjud kinolar:\n{msg}")
    else:
        await message.answer("Hozircha kino yo‘q.")

# Bot ishga tushurish
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)