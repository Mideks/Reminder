from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks import MenuCallbackFactory, ConfirmRemindCreationButton


def get_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Новое напоминание", callback_data=MenuCallbackFactory(action="new_reminder"))
    builder.button(text="Список напоминаний", callback_data=MenuCallbackFactory(action="reminder_list"))

    return builder.as_markup()


def get_confirm_remind_creation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="📝 Изменить текст",
                   callback_data=ConfirmRemindCreationButton(action="change_text"))
    builder.button(text="⏳ Изменить время",
                   callback_data=ConfirmRemindCreationButton(action="change_time"))
    builder.button(text="✅ Всё верно",
                   callback_data=ConfirmRemindCreationButton(action="confirm"))

    builder.adjust(2, 1)

    return builder.as_markup()



