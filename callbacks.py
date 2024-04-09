import dataclasses
import enum

from aiogram.filters.callback_data import CallbackData


class ActionButtonAction(enum.Enum):
    confirm_remind_creation = "confirm_remind_creation"
    edit_remind_time = "edit_remind_time"
    edit_remind_text = "edit_remind_text"
    remind_list = "remind_list"
    new_remind = "new_remind"


class ActionButton(CallbackData, prefix="action"):
    action: ActionButtonAction


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

