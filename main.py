import logging
import asyncio
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.input_file import FSInputFile
from aiogram.filters.command import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import TOKEN, ADMIN_ID
from database import init_video_table, add_video, get_video, add_user, init_user_table, get_all_users


# Turn on logging.
# This will help in debugging and tracking the bot's activity
# and errors.
logging.basicConfig(level=logging.INFO)

# Initialize the database
# and create the video table if it doesn't exist
init_video_table()

# Initialize the user table
# and create it if it doesn't exist
init_user_table()

# Initilization of bot and dispatcher
# The bot token is used to authenticate the bot with Telegram API
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

# List of required channels
# This list contains the usernames of channels that users must subscribe to
# before using the bot.
REQUIRED_CHANNELS = ["@testforbottttttt"]


# This class defines the states for the bot's conversation.
class AddVideo(StatesGroup):
    waiting_code = State()
    waiting_video = State()


# Subscribtion checker
# This function checks if a user is subscribed to the required channels.
# It takes a user ID as a parameter and returns True if the user is subscribed
# to all required channels, otherwise returns False.
async def is_subscribed(user_id: int) -> bool:
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)

            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False

    return True


# Command handler for /start
# This function is triggered when a user sends the /start command.
# It checks if the user is subscribed to the required channels.
# If the user is subscribed, it sends a welcome message.
# If not, it sends a message with buttons to subscribe to the channels.
@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    answer = await is_subscribed(user_id=user_id)
    add_user(user_id, full_name, username)

    if answer:
        await message.answer(f"Hi {message.from_user.full_name}! Welcome, type film code:")

    else:
        channel_number = 1
        keyboards = []
        for channel in REQUIRED_CHANNELS:
            button = InlineKeyboardButton(
                text=f"{channel_number}. Kanal",
                url=f"https://t.me/{channel.lstrip('@')}"
            )
            keyboards.append([button])
            channel_number += 1

        button = InlineKeyboardButton(
            text="Done",
            callback_data="done"
        )
        keyboards.append([button])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboards)

        await message.answer(
            "You are not subscribed to the required channels. Please subscribe to continue.",
            reply_markup=keyboard
        )


# Callback handler for "done" button
# This function is triggered when the user clicks the "done" button.
# It checks if the user is subscribed to the required channels.
# If the user is subscribed, it sends a welcome message.
# If not, it sends a message with buttons to subscribe to the channels.
@dp.callback_query()
async def callback_done(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    answer = await is_subscribed(user_id=user_id)
    callback_data = callback.data

    if callback_data == "done":
        if answer:
            await callback.message.answer("Welcome! Type film code:")
        else:
            channel_number = 1
            keyboards = []
            for channel in REQUIRED_CHANNELS:
                button = InlineKeyboardButton(
                    text=f"{channel_number}. Kanal",
                    url=f"https://t.me/{channel.lstrip('@')}"
                )
                keyboards.append([button])
                channel_number += 1

            button = InlineKeyboardButton(
                text="Done",
                callback_data="done"
            )
            keyboards.append([button])
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboards)

            await callback.message.answer(
                "You are not subscribed to the required channels. Please subscribe to continue.",
                reply_markup=keyboard
            )


@dp.message(Command("users"))
async def list_users(message: types.Message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        await message.answer("You don't have permission.")
        return

    users = get_all_users()
    if not users:
        await message.answer("No user's.")
        return

    text_lines = []
    for user in users:
        _, user_id, full_name, username, created_at, is_active = user
        username_text = f"@{username}" if username else "no username"
        status = "Active" if is_active else "not active"
        text_lines.append(f"{status} {full_name} ({username_text}) - ID: {user_id}")

    full_text = "\n".join(text_lines)

    if len(full_text) > 4000:
        await message.answer("So many information for one message!")

    else:
        await message.answer(full_text)


# This function is triggered when a user sends a message with a film code.
# It retrieves the video associated with the code from the database.
# If the video is found, it sends the video file to the user.
# If the video is not found, it sends a message indicating that no video was found.
# It uses the get_video function from the database module to retrieve the video.
# The function checks if the file exists before sending it to the user.
# If the file exists, it uses FSInputFile to send the file.
@dp.message(F.text)
async def get_video_by_code(message: types.Message):
    code = message.text
    result = get_video(code)
    user_id = message.from_user.id
    answer = await is_subscribed(user_id=user_id)


    if answer:
        if result:
            file_path = result[0]

            # Check if the file exists
            if os.path.exists(file_path):

                try:
                    # Pass the file path directly to InputFile
                    file = FSInputFile(file_path, filename=os.path.basename(file_path))
                    await message.answer_document(file)  # Send the file

                except Exception as e:
                    print(f"Error sending file: {e}")
                    await message.answer("An error occurred while sending the video. Please try again later.")

            else:
                await message.answer("The video file could not be found. Please contact the administrator.")

        else:
            await message.answer("No video found with this code.")

    else:
        channel_number = 1
        keyboards = []
        for channel in REQUIRED_CHANNELS:
            button = InlineKeyboardButton(
                text=f"{channel_number}. Kanal",
                url=f"https://t.me/{channel.lstrip('@')}"
            )
            keyboards.append([button])
            channel_number += 1

        button = InlineKeyboardButton(
            text="Done",
            callback_data="done"
        )
        keyboards.append([button])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboards)

        await message.answer(
            "You are not subscribed to the required channels. Please subscribe to continue.",
            reply_markup=keyboard
        )


# This function is triggered when a user sends the /addvideo command.
# It checks if the user is an admin (using the ADMIN_ID).
# If the user is an admin, it sets the state to waiting_code
# and asks the user to send the film code.
@dp.message(Command("addvideo"))
async def add_video_command(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("You are not authorized to use this command.")
        return

    await state.set_state(AddVideo.waiting_code)
    await message.answer("Please send the film code:")


# This function is triggered when the user sends a message with the film code.
# It updates the state to waiting_video and asks the user to send the video file.
# It uses the FSMContext to manage the state of the conversation.
@dp.message(AddVideo.waiting_code)
async def get_video_code(message: types.Message, state: FSMContext):
    await state.update_data(code=message.text)
    await state.set_state(AddVideo.waiting_video)
    await message.answer("Please send the video file:")


# This function is triggered when the user sends a video file.
# It retrieves the code from the state and saves the video file to the database.
@dp.message(AddVideo.waiting_video, F.video)
async def get_video_file(message: types.Message, state: FSMContext):
    if not message.video:
        await message.answer("Please send a video file.")
        return
    
    data = await state.get_data()
    code = data.get("code")

    file = message.video
    file_path = f"videos/{code}.mp4"

    file_info = await message.bot.get_file(file.file_id)
    await message.bot.download_file(file_info.file_path, file_path)

    result = add_video(code, file_path)

    if result:
        await message.answer("Video added successfully.")
    else:
        await message.answer("Video with this code already exists.")
    
    await state.clear()


# Start polling process
# This function starts the bot and begins polling for updates.
# It uses the Dispatcher to handle incoming messages and commands.
# The bot will run until it is stopped manually or an error occurs.
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
