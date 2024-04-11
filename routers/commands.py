from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery

import callbacks
from keyboards import get_menu_keyboard

router = Router()


@router.message(Command('test'))
async def test_command(message: Message):
    pass


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Привет! Я бот напоминалка", reply_markup=get_menu_keyboard())


@router.callback_query(callbacks.NavigateButton.filter(F.location == callbacks.NavigateButtonLocation.main_menu))
async def send_start_menu(callback: CallbackQuery):
    await callback.message.edit_text("Привет! Я бот напоминалка", reply_markup=get_menu_keyboard())
    await callback.answer()