from typing import Callable

from aiogram import Bot

from main import bot


async def send_remind(chat_id: str, remind_text: str) -> None:
    message_text = ("🔔 Вам новое напоминание!\n"
                    f"💬: {remind_text}")
    await bot.send_message(chat_id, message_text)

