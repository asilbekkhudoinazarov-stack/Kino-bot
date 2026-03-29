from aiogram import Bot
from config import CHANNEL_ID

async def is_subscribed(user_id, bot: Bot):
    member = await bot.get_chat_member(CHANNEL_ID, user_id)
    return member.status != "left"