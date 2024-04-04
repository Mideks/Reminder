from datetime import datetime

import aiogram
from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import sessionmaker, Session

import states
import time_parser
from callbacks import ActionButton
from entities import Remind
from keyboards import get_confirm_remind_creation_keyboard

from tasks import send_remind

router = Router()


@router.callback_query(ActionButton.filter(F.action == "new_reminder"))
async def enter_remind_creation(
        callback: types.CallbackQuery, callback_data: ActionButton,
        state: FSMContext):
    await callback.message.reply(
        "Давай создадим новое напоминание! Для начала введи текст напоминания")
    # Переходим к состоянию "ожидаю ввода текста напоминания"
    await state.set_state(states.CreateNewReminder.entering_text)
    await callback.answer()  # чтобы кнопка не зависала


@router.message(states.CreateNewReminder.entering_text)
async def enter_remind_text(message: Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)  # Здесь мы сохраняем введенный текст

    await message.reply("Окей, теперь давай определимся со временем\n"
                        "Вы можете ввести время в свободной форме, или в формате DD/MM hh:mm")
    # Переходим к состоянию "ожидаю ввода времени напоминания"
    await state.set_state(states.CreateNewReminder.entering_time)


@router.message(states.CreateNewReminder.entering_time)
async def enter_remind_date(message: Message, state: FSMContext):
    time = message.text

    parsed_time = time_parser.time_parser(time)
    if parsed_time is None:
        await message.reply("Неверный формат даты! Попробуйте ещё раз")
        return
    await state.update_data(time=parsed_time)  # сохраняем введённую дату
    await state.update_data(entering_time=datetime.now())

    # получаем ранее записанные данные
    data = await state.get_data()
    await message.reply(
        "Почти готов, давай проверим, всё ли правильно?\n\n"
        f"Напоминание будет <b>{parsed_time.strftime('%d %B в %H:%M:%S')}</b>\n"
        f"{data['text']}",
        reply_markup=get_confirm_remind_creation_keyboard()
    )

    # Переходим к состоянию "подтверждение создания"
    await state.set_state(states.CreateNewReminder.confirm_creation)


@router.callback_query(ActionButton.filter(F.action == "confirm_remind_creation"))
async def confirm_remind_creation(
        callback: types.CallbackQuery, callback_data: ActionButton,
        state: FSMContext, scheduler: AsyncIOScheduler, db_session: sessionmaker[Session]):
    # Получаем контекст
    data = await state.get_data()

    # Считаем время напоминания с учётом времени отправки сообщения
    real_time: datetime = data['time'] + (datetime.now() - data['entering_time'])
    # Добавить напоминание в планировщик
    job = scheduler.add_job(send_remind, "date", run_date=real_time,
                            args=(callback.message.chat.id, data["text"]))

    with db_session() as session:
        new_remind = Remind(user_id=callback.message.chat.id, remind_date=real_time,
                            title="", text=data["text"], scheduler_job_id=job.id)
        session.add(new_remind)
        session.commit()

    # Отправить сообщение
    await callback.message.answer("☑️ Напоминание успешно создано")
    await callback.answer()
