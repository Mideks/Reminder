import dataclasses
import enum
from typing import Optional

from aiogram.filters.callback_data import CallbackData


class ActionButtonAction(enum.Enum):
    confirm_remind_creation = "confirm_remind_creation"
    edit_remind_time = "edit_remind_time"
    edit_remind_text = "edit_remind_text"
    remind_list = "remind_list"
    new_remind = "new_remind"
    new_group_remind = 'new_group_remind'
    show_group_list = "show_group_list"
    show_group = "show_group"
    remind_group_member_management = "remind_group_member_management"
    change_remind_group_name = "change_remind_group_name"
    leave_from_remind_group = "leave_from_remind_group"
    delete_remind_group = "delete_remind_group"
    show_remind_groups_list = "show_remind_groups_list"
    select_group_for_new_remind = "select_group_for_new_remind"
    show_menu = "show_menu"
    edit_remind_group = "edit_remind_group"
    edit_group_for_new_remind = "edit_group_for_new_remind"
    show_confirm_remind_creation_menu = "show_confirm_remind_creation_menu"
    create_remind_group = "create_remind_group"
    show_help_section = "show_help_section"
    approve_all_reminds = "approve_all_reminds"
    edit_raw_remind = "edit_raw_remind"
    back_to_raw_remind_list = "back_to_raw_remind_list"
    create_remind_from_voice = "create_remind_from_voice"


class ActionButton(CallbackData, prefix="action"):
    action: ActionButtonAction
    data: Optional[str] = None


class RemindButtonAction(enum.Enum):
    show = "show"
    delete = "delete"
    edit_text = "edit_text"
    edit_time = "edit_time"


class RemindButton(CallbackData, prefix="remind"):
    remind_id: int
    action: RemindButtonAction


class NavigateButtonLocation(enum.Enum):
    main_menu = "main_menu"
    remind_list = "remind_list"


class NavigateButton(CallbackData, prefix="navigate"):
    location: NavigateButtonLocation

