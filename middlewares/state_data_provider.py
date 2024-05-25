from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject

from states.state_data import StateData


class StateDataProvider(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        state: FSMContext = data["state"]
        data_ = await state.get_data()
        data["state_data"] = data_.get("state_data", StateData())

        result = await handler(event, data)
        await state.update_data(state_data=data["state_data"])
        return result
