from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks import ActionButton, RemindButton, RemindButtonAction, NavigateButton, NavigateButtonLocation, \
    ActionButtonAction
from entities.remind import Remind


def get_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Новое напоминание", callback_data=ActionButton(action=ActionButtonAction.new_remind))
    builder.button(text="Список напоминаний", callback_data=ActionButton(action=ActionButtonAction.remind_list))

    return builder.as_markup()


def get_confirm_remind_creation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="📝 Изменить текст",
                   callback_data=ActionButton(action=ActionButtonAction.edit_remind_text))
    builder.button(text="⏳ Изменить время",
                   callback_data=ActionButton(action=ActionButtonAction.edit_remind_time))
    builder.button(text="✅ Всё верно",
                   callback_data=ActionButton(action=ActionButtonAction.confirm_remind_creation))

    builder.adjust(2, 1)

    return builder.as_markup()


def get_remind_list_keyboard(reminds: list[Remind]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for i, remind in enumerate(reminds, 1):
        r = RemindButton(remind_id=remind.id, action=RemindButtonAction.show)
        builder.button(text=f"{i}. {remind.text}",
                       callback_data=r)

    builder.button(text="🔙 Назад в меню",
                   callback_data=NavigateButton(location=NavigateButtonLocation.main_menu))
    builder.adjust(1)

    return builder


def get_remind_menu_markup(remind: Remind) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Удалить",
                   callback_data=RemindButton(remind_id=remind.id, action=RemindButtonAction.delete))
    builder.button(text="Редактировать текст",
                   callback_data=RemindButton(remind_id=remind.id, action=RemindButtonAction.edit_text))
    builder.button(text="Редактировать время",
                   callback_data=RemindButton(remind_id=remind.id, action=RemindButtonAction.edit_time))
    builder.button(text="🔙 Назад к списку",
                   callback_data=NavigateButton(location=NavigateButtonLocation.remind_list))
    builder.adjust(1)

    return builder