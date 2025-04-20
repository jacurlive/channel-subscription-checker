import logging
import asyncio
import os

from aiogram import types, F
from aiogram.types.input_file import FSInputFile
from aiogram.filters.command import CommandStart, Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from loader import bot, dp
from state import AddVideo, MessageForAll
from utils import is_subscribed, required_channel_list
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

# List of required channels
# This list contains the usernames of channels that users must subscribe to
# before using the bot.
REQUIRED_CHANNELS = ["@testforbottttttt"]


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
    answer = await is_subscribed(user_id=user_id, REQUIRED_CHANNELS=REQUIRED_CHANNELS)
    add_user(user_id, full_name, username)

    if answer:
        await message.answer(f"Привет {message.from_user.full_name}! Напиши код фильма:")

    else:
        await required_channel_list(user_id=user_id, REQUIRED_CHANNELS=REQUIRED_CHANNELS)


# Callback handler for "done" button
# This function is triggered when the user clicks the "done" button.
# It checks if the user is subscribed to the required channels.
# If the user is subscribed, it sends a welcome message.
# If not, it sends a message with buttons to subscribe to the channels.
@dp.callback_query()
async def callback_done(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    answer = await is_subscribed(user_id=user_id, REQUIRED_CHANNELS=REQUIRED_CHANNELS)
    callback_data = callback.data

    if callback_data == "done":
        if answer:
            await callback.message.answer("Напишите код фильма:")
        else:
            await required_channel_list(user_id=user_id, REQUIRED_CHANNELS=REQUIRED_CHANNELS)


# This function is triggered when the user sends the /users command.
# It checks if the user is an admin (using the ADMIN_ID).
# If the user is an admin, it retrieves all users from the database
# and sends a list of users with their status (active or not active).
@dp.message(Command("users"))
async def list_users(message: types.Message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        await message.answer("У вас нет прав для использования этой команды.")
        return

    users = get_all_users()
    if not users:
        await message.answer("Нет пользователей в базе данных.")
        return

    text_lines = []
    for user in users:
        _, user_id, full_name, username, created_at, is_active = user
        username_text = f"@{username}" if username else "no username"
        status = "Active" if is_active else "not active"
        text_lines.append(f"{status} {full_name} ({username_text}) - ID: {user_id}")

    full_text = "\n".join(text_lines)

    if len(full_text) > 4000:
        await message.answer("Много пользователей, не могу отправить сообщение.")

    else:
        await message.answer(full_text)


# This function is triggered when the user sends the /messageforall command.
# It checks if the user is an admin (using the ADMIN_ID).
# If the user is an admin, it sets the state to waiting_message
# and asks the user to send the message to all users.
@dp.message(Command("messageforall"))
async def message_all_users(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав для использования этой команды.")
        return
    
    await message.answer("Отправьте сообщение всем пользователям:")
    await state.set_state(MessageForAll.waiting_message)


# This function is triggered when the user sends a message to all users.
# It retrieves all users from the database and sends the message to each user.
# If the message is sent successfully, it sends a confirmation message.
# If the message fails to send, it sends a failure message.
@dp.message(MessageForAll.waiting_message)
async def send_message_to_all_users(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав для использования этой команды.")
        return

    users = get_all_users()
    sent = 0
    failed = 0

    if not users:
        await message.answer("Нет пользователей в базе данных.")
        return

    for user in users:
        user_id = user[1]

        try:
            await message.copy_to(chat_id=user_id)
            sent += 1
        except Exception as e:
            print(f"Ошибка при отправке сообщения этому пользователю: {user_id}: {e}")
            await message.answer(f"Ошибка при отправке сообщения этому пользователю: {user_id}.")
            failed += 1
    
    await message.answer(f"Сообщение отправлено {sent} пользователям, не удалось отправить {failed} пользователям.")
    await state.clear()


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
    answer = await is_subscribed(user_id=user_id, REQUIRED_CHANNELS=REQUIRED_CHANNELS)


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
                    print(f"Ошибка при отправке видео: {e}")
                    await message.answer("Произошла ошибка при отправке видео. Пожалуйста, попробуйте позже.")

            else:
                await message.answer("Видео не найдено. Пожалуйста, проверьте код фильма и попробуйте снова.")

        else:
            await message.answer("Видео не найдено. Пожалуйста, проверьте код фильма и попробуйте снова.")

    else:
        await required_channel_list(user_id=user_id, REQUIRED_CHANNELS=REQUIRED_CHANNELS)


# This function is triggered when a user sends the /addvideo command.
# It checks if the user is an admin (using the ADMIN_ID).
# If the user is an admin, it sets the state to waiting_code
# and asks the user to send the film code.
@dp.message(Command("addvideo"))
async def add_video_command(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав для использования этой команды.")
        return

    await state.set_state(AddVideo.waiting_code)
    await message.answer("Отправьте код фильма:")


# This function is triggered when the user sends a message with the film code.
# It updates the state to waiting_video and asks the user to send the video file.
# It uses the FSMContext to manage the state of the conversation.
@dp.message(AddVideo.waiting_code)
async def get_video_code(message: types.Message, state: FSMContext):
    await state.update_data(code=message.text)
    await state.set_state(AddVideo.waiting_video)
    await message.answer("Отправьте видео файл:")


# This function is triggered when the user sends a video file.
# It retrieves the code from the state and saves the video file to the database.
@dp.message(AddVideo.waiting_video, F.video)
async def get_video_file(message: types.Message, state: FSMContext):
    if not message.video:
        await message.answer("Отправьте видео файл.")
        return
    
    data = await state.get_data()
    code = data.get("code")

    file = message.video
    file_path = f"videos/{code}.mp4"

    file_info = await message.bot.get_file(file.file_id)
    await message.bot.download_file(file_info.file_path, file_path)

    result = add_video(code, file_path)

    if result:
        await message.answer("Видео успешно добавлено.")
    else:
        await message.answer("Видео с таким кодом уже существует.")
    
    await state.clear()


# Start polling process
# This function starts the bot and begins polling for updates.
# It uses the Dispatcher to handle incoming messages and commands.
# The bot will run until it is stopped manually or an error occurs.
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
