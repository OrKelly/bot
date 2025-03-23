from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from entities.users import User
from exceptions.users import UserNotFoundException
from keyboards.main import get_main_keyboard
from messages.greeting import WELCOME_NEW_USER, WELCOME_OLD_USER
from repositories.users import UserRepository

router = Router()


@router.message(Command("start"))
async def startup_handler(message: Message):
    user = User.from_message(message)
    try:
        user = await UserRepository().get_user_by_user_id(user.user_id)
        text = WELCOME_OLD_USER
    except UserNotFoundException:
        await UserRepository().create_user(user)
        text = WELCOME_NEW_USER
    await message.answer(text, reply_markup=get_main_keyboard())
