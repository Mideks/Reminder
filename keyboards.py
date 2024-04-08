from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks import ActionButton, RemindButton
from entities.remind import Remind


def get_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Новое напоминание", callback_data=ActionButton(action="new_reminder"))
    builder.button(text="Список напоминаний", callback_data=ActionButton(action="remind_list"))

    return builder.as_markup()


def get_confirm_remind_creation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="📝 Изменить текст",
                   callback_data=ActionButton(action="change_remind_text"))
    builder.button(text="⏳ Изменить время",
                   callback_data=ActionButton(action="change_remind_time"))
    builder.button(text="✅ Всё верно",
                   callback_data=ActionButton(action="confirm_remind_creation"))

    builder.adjust(2, 1)

    return builder.as_markup()


def get_remind_list_keyboard(reminds: list[Remind]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for i, remind in enumerate(reminds, 1):
        builder.button(text=f"{i}. {remind.text}", callback_data=RemindButton(remind_id=remind.id))
    builder.adjust(1)

    return builder
