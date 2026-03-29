from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import TOKEN, ADMINS
from database import add_user, movies
from keyboards import start_kb, admin_kb
from utils import is_subscribed
from admin_panel import add_new_movie, delete_movie

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    add_user(message.from_user.id)
    
    if not await is_subscribed(message.from_user.id, bot):
        await message.answer("Obuna bo'ling: @SizningKanalingiz")
        return
    
    if message.from_user.id in ADMINS:
        await message.answer("Admin panelga xush kelibsiz", reply_markup=admin_kb)
    else:
        await message.answer("Botga xush kelibsiz!", reply_markup=start_kb)

@dp.message_handler(lambda m: m.text == "Kino kodi yuborish")
async def kodni_qabul_qilish(message: types.Message):
    await message.answer("Kod kiriting:")

@dp.message_handler()
async def kino_berish(message: types.Message):
    user_input = message.text.strip().upper()
    if user_input in movies:
        path = movies[user_input]
        await message.answer_document(open(path, "rb"))
    else:
        await message.answer("Bunday kod topilmadi.")

@dp.message_handler(lambda m: m.from_user.id in ADMINS)
async def admin_panel(message: types.Message):
    text = message.text
    if text == "Kino qo'shish":
        await message.answer("Kod va fayl nomini kiriting: KOD, fayl.txt")
    elif text == "Kino o'chirish":
        await message.answer("O'chirish uchun kod kiriting:")
    elif text == "Statistika":
        await message.answer(f"Foydalanuvchilar soni: {len(users)}\nKino soni: {len(movies)}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)