import asyncio
import locale
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

import entities
from entities.base import Base
from routers import create_remind, commands, remind_list

# Для верного отображения дат
locale.setlocale(locale.LC_TIME, 'ru_RU')

TOKEN = getenv("BOT_TOKEN")
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

# Создали планировщик
scheduler = AsyncIOScheduler()

# setup data storage
url = 'sqlite:///db.sqlite'
scheduler.add_jobstore('sqlalchemy', url=url)
engine = create_engine(url, echo=False)
db_session: sessionmaker[Session] = sessionmaker(bind=engine)
# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


async def main() -> None:
    # Запуск планировщика тут!!
    scheduler.start()

    # задаём нужные контекстные переменные
    dp["db_session"] = db_session
    dp["scheduler"] = scheduler

    # подключаем роутеры
    dp.include_router(commands.router)
    dp.include_router(create_remind.router)
    dp.include_router(remind_list.router)


    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
