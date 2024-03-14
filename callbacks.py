from aiogram.filters.callback_data import CallbackData


class ActionButton(CallbackData, prefix="action"):
    action: str

