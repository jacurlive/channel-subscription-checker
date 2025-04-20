from aiogram import Bot, Dispatcher

from config import TOKEN, ADMIN_ID


# Initilization of bot and dispatcher
# The bot token is used to authenticate the bot with Telegram API
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)
