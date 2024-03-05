from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks import MenuCallbackFactory


def get_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Новое напоминание", callback_data=MenuCallbackFactory(action="new_reminder"))
    builder.button(text="Список напоминаний", callback_data=MenuCallbackFactory(action="reminder_list"))

    return builder.as_markup()

