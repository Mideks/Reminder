import dataclasses

from aiogram.filters.callback_data import CallbackData


class ActionButton(CallbackData, prefix="action"):
    action: str


class RemindButton(CallbackData, prefix="remind"):
    remind_id: int