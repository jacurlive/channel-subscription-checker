from aiogram.fsm.state import State, StatesGroup


# This class defines the states for the bot's conversation.
class AddVideo(StatesGroup):
    waiting_code = State()
    waiting_video = State()


# This class defines the states for the bot's conversation.
class MessageForAll(StatesGroup):
    waiting_message = State()
