import dataclasses
import enum

from aiogram.filters.callback_data import CallbackData


class ActionButton(CallbackData, prefix="action"):
    action: str


class RemindButtonAction(enum.Enum):
    show = "show"
    delete = "delete"
    edit_text = "edit_text"
    edit_time = "edit_time"


class RemindButton(CallbackData, prefix="remind"):
    remind_id: int
    action: str


class NavigateButtonLocation(enum.Enum):
    main_menu = "main_menu"
    remind_list = "remind_list"


class NavigateButton(CallbackData, prefix="navigate"):
    location: NavigateButtonLocation

