import asyncio
import locale
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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import entities
import states
import time_parser
from callbacks import ActionButton
from entities import Remind
from keyboards import get_menu_keyboard, get_confirm_remind_creation_keyboard

# Для верного отображения дат
locale.setlocale(locale.LC_TIME, 'ru_RU')

TOKEN = getenv("BOT_TOKEN")
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

# Создали планировщик
scheduler = AsyncIOScheduler()

# setup data storage
url = 'sqlite:///example.sqlite'
scheduler.add_jobstore('sqlalchemy', url=url)
engine = create_engine(url, echo=False)
Session = sessionmaker(bind=engine)
# entities.Base.metadata.drop_all(engine)
entities.Base.metadata.create_all(engine)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Привет! Я бот напоминалка",
                         reply_markup=get_menu_keyboard())


# Вход в создание напоминаний
@dp.callback_query(ActionButton.filter(F.action == "new_reminder"))
async def enter_remind_creation(
        callback: types.CallbackQuery, callback_data: ActionButton,
        state: FSMContext):

    await callback.message.reply(
        "Давай создадим новое напоминание! Для начала введи текст напоминания")
    # Переходим к состоянию "ожидаю ввода текста напоминания"
    await state.set_state(states.CreateNewReminder.entering_text)
    await callback.answer()  # чтобы кнопка не зависала


@dp.message(states.CreateNewReminder.entering_text)
async def enter_remind_text(message: Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)  # Здесь мы сохраняем введенный текст

    await message.reply("Окей, теперь давай определимся со временем\n"
                        "Вы можете ввести время в свободной форме, или в формате DD/MM hh:mm")
    # Переходим к состоянию "ожидаю ввода времени напоминания"
    await state.set_state(states.CreateNewReminder.entering_time)


@dp.message(states.CreateNewReminder.entering_time)
async def enter_remind_text(message: Message, state: FSMContext):
    time = message.text

    parsed_time = time_parser.time_parser(time)
    if parsed_time is None:
        await message.reply("Неверный формат даты! Попробуйте ещё раз")
        return
    await state.update_data(time=parsed_time)  # сохраняем введённую дату

    # получаем ранее записанные данные
    data = await state.get_data()
    await message.reply(
        "Напоминание создано, давай проверим, всё ли правильно?\n\n"
        f"Напоминание будет <b>{parsed_time.strftime('%d %B в %H:%M:%S')}</b>\n"
        f"{data['text']}",
        reply_markup=get_confirm_remind_creation_keyboard()
    )

    # Переходим к состоянию "подтверждение создания"
    await state.set_state(states.CreateNewReminder.confirm_creation)


async def send_remind(chat_id: str, remind_text: str):
    message_text = ("🔔 Вам новое напоминание!\n"
                    f"💬: {remind_text}")
    await bot.send_message(chat_id, message_text)


@dp.callback_query(ActionButton.filter(F.action == "confirm_remind_creation"))
async def confirm_remind_creation(
        callback: types.CallbackQuery, callback_data: ActionButton,
        state: FSMContext):
    # Получаем контекст
    data = await state.get_data()

    # Добавить напоминание в планировщик
    job = scheduler.add_job(send_remind, "date", run_date=data["time"],
                            args=(callback.message.chat.id, data["text"]))

    with Session() as session:
        new_remind = Remind(user_id=callback.message.chat.id, remind_date=data["time"],
                            title="", text=data["text"], scheduler_job_id=job.id)
        session.add(new_remind)
        session.commit()

    # Отправить сообщение
    await callback.message.answer("☑️ Напоминание успешно создано")
    await callback.answer()


@dp.message(F.text == "/test")
async def test_command(message: Message):
    pass


async def main() -> None:
    # Запуск планировщика тут!!
    scheduler.start()

    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
