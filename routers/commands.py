from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from keyboards import get_menu_keyboard

router = Router()


@router.message(Command('test'))
async def test_command(message: Message):
    pass


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Привет! Я бот напоминалка", reply_markup=get_menu_keyboard())
