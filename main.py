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
from context import Context
from entities.base import Base
from middlewares.session_creator import SessionCreatorMiddleware
from middlewares.state_data_provider import StateDataProvider
from routers import create_remind, commands, remind_list, manage_groups

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

    # задаём контекст для бота
    context = Context(db_session, scheduler)
    dp["context"] = context
    dp.update.middleware.register(SessionCreatorMiddleware())
    dp.update.middleware.register(StateDataProvider())

    # подключаем роутеры
    dp.include_router(commands.router)
    dp.include_router(manage_groups.router)
    dp.include_router(create_remind.router)
    dp.include_router(remind_list.router)


    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
