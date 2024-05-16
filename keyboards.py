from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import texts.buttons
from callbacks import ActionButton, RemindButton, RemindButtonAction, NavigateButton, NavigateButtonLocation, \
    ActionButtonAction
from entities.remind import Remind
from entities.remind_group import RemindGroup


def get_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Новое напоминание", callback_data=ActionButton(action=ActionButtonAction.new_remind))
    builder.button(text="Новое групповое напоминание",
                   callback_data=ActionButton(action=ActionButtonAction.new_group_remind))
    builder.button(text="Список напоминаний", callback_data=ActionButton(action=ActionButtonAction.remind_list))
    builder.adjust(1, 1)
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


def get_groups_list_keyboard(groups: list[RemindGroup]) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    for group in groups:
        text = f"{group.name} (#{group.id})"
        kb.button(text=text,
                  callback_data=ActionButton(action=ActionButtonAction.show_group, data=f"{group.id}"))
    kb.adjust(1)
    return kb


def get_grop_management_keyboard(group: RemindGroup, is_owner: bool = False) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()

    kb.button(text=texts.buttons.leave_from_remind_group,
              callback_data=ActionButton(action=ActionButtonAction.leave_from_remind_group, data=f"{group.id}"))
    kb.button(text=texts.buttons.change_remind_group_name,
              callback_data=ActionButton(action=ActionButtonAction.change_remind_group_name, data=f"{group.id}"))
    kb.button(text=texts.buttons.remind_group_member_management,
              callback_data=ActionButton(action=ActionButtonAction.remind_group_member_management, data=f"{group.id}"))
    if is_owner:
        kb.button(text=texts.buttons.delete_remind_group,
                  callback_data=ActionButton(action=ActionButtonAction.delete_remind_group, data=f"{group.id}"))
    kb.button(text=texts.buttons.back_to_group_list,
              callback_data=ActionButton(action=ActionButtonAction.show_group_list))

    kb.adjust(1)

    return kb