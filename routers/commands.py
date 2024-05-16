import re

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import Session

import callbacks
import texts.messages
from context import Context
from entities.user import update_user
from keyboards import get_menu_keyboard

router = Router()


@router.message(CommandStart(magic=~F.args))
async def command_start_handler(message: Message, db_session: Session) -> None:
    await message.answer("Привет! Я бот напоминалка", reply_markup=get_menu_keyboard())
    user = message.from_user
    update_user(db_session, user.id, user.first_name, user.last_name)


@router.message(Command("cancel"))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(texts.messages.cancel_command)


@router.callback_query(callbacks.NavigateButton.filter(F.location == callbacks.NavigateButtonLocation.main_menu))
async def send_start_menu(callback: CallbackQuery):
    await callback.message.edit_text("Привет! Я бот напоминалка", reply_markup=get_menu_keyboard())
    await callback.answer()
