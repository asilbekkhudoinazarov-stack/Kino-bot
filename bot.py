import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
import json

API_TOKEN = '8735477684:AAE0vS34otIUJFHehfqCWslivG-j_vFK7gc'
ADMIN_IDS = [7310599180, 5977950655]  # Bu yerga admin telegram IDlarini yozing
CHANNEL_USERNAME = "@SIZNING_KANAL"  # Majburiy obuna kanali

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Foydalanuvchilarni va kinolarni saqlash (odatda db.py ishlatamiz)
users_data = {}
movies_data = {}

# Klaviaturalar
def main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Obunani tekshir"))
    return keyboard

def admin_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Kino qo'sh"))
    keyboard.add(KeyboardButton("Kinolar ro'yxati"))
    return keyboard

# Majburiy obuna tekshirish
async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status != "left"
    except:
        return False

# Start komandasi
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    users_data[message.from_user.id] = {"subscribed": False}
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Salom Admin! Panelga xush kelibsiz.", reply_markup=admin_keyboard())
    else:
        await message.answer(
            f"Assalomu alaykum! Botdan foydalanish uchun kanalimizga obuna bo'ling: {CHANNEL_USERNAME}",
            reply_markup=main_keyboard()
        )

# Obuna tekshirish tugmasi
@dp.message_handler(Text("Obunani tekshir"))
async def check_subscription(message: types.Message):
    subscribed = await is_subscribed(message.from_user.id)
    users_data[message.from_user.id]["subscribed"] = subscribed
    if subscribed:
        await message.answer("Siz obuna bo'lgansiz! Endi kinolarni ko'rishingiz mumkin.")
    else:
        await message.answer(f"Iltimos, kanalimizga obuna bo'ling: {CHANNEL_USERNAME}")

# Admin: Kino qo'shish
@dp.message_handler(lambda message: message.from_user.id in ADMIN_IDS, Text("Kino qo'sh"))
async def admin_add_movie(message: types.Message):
    await message.answer("Kino nomini yozing:")

    @dp.message_handler(lambda m: m.from_user.id in ADMIN_IDS)
    async def get_movie_name(name_msg: types.Message):
        movie_name = name_msg.text
        movies_data[movie_name] = {"file_id": None}
        await name_msg.answer("Kino faylini yuboring (video):")

        @dp.message_handler(lambda m: m.from_user.id in ADMIN_IDS, content_types=["video"])
        async def get_movie_file(file_msg: types.Message):
            movies_data[movie_name]["file_id"] = file_msg.video.file_id
            await file_msg.answer(f"{movie_name} kino muvaffaqiyatli qo'shildi!")

# Foydalanuvchiga kino yuborish
@dp.message_handler(lambda message: message.from_user.id not in ADMIN_IDS)
async def send_movies(message: types.Message):
    subscribed = users_data.get(message.from_user.id, {}).get("subscribed", False)
    if not subscribed:
        await message.answer(f"Iltimos, kanalimizga obuna bo'ling: {CHANNEL_USERNAME}")
        return

    if not movies_data:
        await message.answer("Hozircha kinolar mavjud emas.")
        return

    for movie_name, info in movies_data.items():
        if info["file_id"]:
            await bot.send_video(message.chat.id, info["file_id"], caption=movie_name)

# Kinolar ro'yxati (admin)
@dp.message_handler(lambda message: message.from_user.id in ADMIN_IDS, Text("Kinolar ro'yxati"))
async def list_movies(message: types.Message):
    if not movies_data:
        await message.answer("Hozircha kinolar mavjud emas.")
    else:
        movies_list = "\n".join(movies_data.keys())
        await message.answer(f"Kinolar:\n{movies_list}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)