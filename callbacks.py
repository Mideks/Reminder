from aiogram.filters.callback_data import CallbackData


class MenuCallbackFactory(CallbackData, prefix="menu"):
    action: str
