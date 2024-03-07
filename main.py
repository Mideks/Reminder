import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import states
from callbacks import MenuCallbackFactory
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


# Вход в создание напоминаний
@dp.callback_query(MenuCallbackFactory.filter(F.action == "new_reminder"))
async def enter_remind_creation(
        callback: types.CallbackQuery, callback_data: MenuCallbackFactory,
        state: FSMContext):

    await callback.message.reply(
        "Давай создадим новое напоминание! Для начала введи текст напоминания")
    # Переходим к состоянию "ожидаю ввода текста напоминания"
    await state.set_state(states.CreateNewReminder.entering_text)
    await callback.answer() # чтобы кнопка не зависала


@dp.message(states.CreateNewReminder.entering_text)
async def enter_remind_text(message: Message, state: FSMContext):
    await message.reply("Окей, теперь давай определимся со временем")

    # Переходим к состоянию "ожидаю ввода времени напоминания"
    await state.set_state(states.CreateNewReminder.entering_time)


@dp.message(states.CreateNewReminder.entering_text)
async def enter_remind_text(message: Message, state: FSMContext):
    await message.reply("Окей, теперь давай определимся со временем")

    # Переходим к состоянию "ожидаю ввода времени напоминания"
    await state.set_state(states.CreateNewReminder.entering_time)


@dp.message(states.CreateNewReminder.entering_time)
async def enter_remind_text(message: Message, state: FSMContext):
    await message.reply("Напоминание создано, давай проверим, всё ли правильно?\n\nНапоминание:\nТекст время")

    # Переходим к состоянию "подтверждение создания"
    await state.set_state(states.CreateNewReminder.confirm_creation)


async def main() -> None:
    # Запуск планировщика тут!!
    scheduler.start()

    # Запускаем бота
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
