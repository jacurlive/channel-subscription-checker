from loader import bot

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Subscribtion checker
# This function checks if a user is subscribed to the required channels.
# It takes a user ID as a parameter and returns True if the user is subscribed
# to all required channels, otherwise returns False.
async def is_subscribed(user_id: int, REQUIRED_CHANNELS: list) -> bool:
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)

            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False

    return True


# This function sends a message to the user with buttons to subscribe to the required channels.
# It takes a user ID and a list of required channels as parameters.
# The buttons will link to the channels, and the user can click them to subscribe.
async def required_channel_list(user_id: int, REQUIRED_CHANNELS: list):
    channel_number = 1
    keyboards = []
    for channel in REQUIRED_CHANNELS:
        button = InlineKeyboardButton(
            text=f"{channel_number}. Канал",
            url=f"https://t.me/{channel.lstrip('@')}"
        )
        keyboards.append([button])
        channel_number += 1

    button = InlineKeyboardButton(
        text="Потвердить✅",
        callback_data="done"
    )
    keyboards.append([button])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboards)

    await bot.send_message(
        chat_id=user_id, text="Для использования бота необходимо подписаться на каналы. Пожалуйста, подпишитесь на каналы ниже:",
        reply_markup=keyboard
    )
