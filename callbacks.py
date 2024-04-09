import dataclasses
import enum

from aiogram.filters.callback_data import CallbackData


class ActionButton(CallbackData, prefix="action"):
    action: str


class RemindButtonAction(enum.Enum):
    show = 1
    delete = 2
    edit_text = 3
    edit_time = 4


class RemindButton(CallbackData, prefix="remind"):
    remind_id: int
    action: str
