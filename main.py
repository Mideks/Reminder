import asyncio
import logging
import sys
from datetime import datetime, timedelta
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from keyboards import get_menu_keyboard

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()

# Создали планировщик
scheduler = AsyncIOScheduler()


# Запланированное задание
async def send_delayed_message(bot, chat_id):
    await bot.send_message(chat_id, "Ещё одно сообщение")


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Привет! Я бот напоминалка",
                         reply_markup=get_menu_keyboard())


async def main() -> None:
    # Запуск планировщика тут!!
    scheduler.start()

    # Запускаем бота
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
