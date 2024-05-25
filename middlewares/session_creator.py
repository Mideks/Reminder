from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from context import Context


class SessionCreatorMiddleware(BaseMiddleware):
    async def __call__(
        self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject, data: Dict[str, Any]
    ) -> Any:
        context: Context = data["context"]
        session = context.db_session_maker()
        data["db_session"] = session
        result = await handler(event, data)
        session.close()
        return result
