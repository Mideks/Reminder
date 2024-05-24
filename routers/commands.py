from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import Session

import callbacks
import keyboards
import texts.messages
from entities.user import update_user
from keyboards import get_menu_keyboard

router = Router()


@router.message(CommandStart(magic=~F.args))
async def command_start_handler(message: Message, db_session: Session) -> None:
    await message.answer(texts.messages.greeting_message, reply_markup=get_menu_keyboard())
    user = message.from_user
    update_user(db_session, user.id, user.first_name, user.last_name)


@router.message(Command("cancel"))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(texts.messages.cancel_command)


@router.callback_query(callbacks.ActionButton.filter(F.action == callbacks.ActionButtonAction.show_menu))
async def send_start_menu(callback: CallbackQuery):
    await callback.message.edit_text(texts.messages.greeting_message, reply_markup=get_menu_keyboard())
    await callback.answer()


@router.callback_query(callbacks.ActionButton.filter(F.action == callbacks.ActionButtonAction.show_help_section))
async def send_start_menu(callback: CallbackQuery):
    await callback.message.edit_text(texts.messages.help_section,
                                     reply_markup=keyboards.get_help_section_keyboard().as_markup())
    await callback.answer()
