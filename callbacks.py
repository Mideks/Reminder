from aiogram.filters.callback_data import CallbackData


class ActionButton(CallbackData, prefix="action"):
    group: str = ""
    action: str

