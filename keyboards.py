from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks import ActionButton


def get_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Новое напоминание", callback_data=ActionButton(action="new_reminder"))
    builder.button(text="Список напоминаний", callback_data=ActionButton(action="reminder_list"))

    return builder.as_markup()


def get_confirm_remind_creation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="📝 Изменить текст",
                   callback_data=ActionButton(action="change_text"))
    builder.button(text="⏳ Изменить время",
                   callback_data=ActionButton(action="change_time"))
    builder.button(text="✅ Всё верно",
                   callback_data=ActionButton(action="confirm"))

    builder.adjust(2, 1)

    return builder.as_markup()



