from typing import Callable

from aiogram import Bot

import entities.remind
from main import bot


async def send_remind(chat_id: str, remind_text: str) -> None:
    # todo: имя группы в текст, если есть
    message_text = ("🔔 Вам новое напоминание!\n"
                    f"💬: {remind_text}")
    # todo: сделать проверку на наличеие группы, и, если есть, то разослать всем в группе
    await bot.send_message(chat_id, message_text)
