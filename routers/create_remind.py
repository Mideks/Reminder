from datetime import datetime
from typing import Optional

import aiogram
from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import sessionmaker, Session

import entities
import keyboards
import states
import remind_parser
import texts
from callbacks import ActionButton, ActionButtonAction
from context import Context
from entities.remind import Remind
from entities.remind_group import send_message_to_remind_group
from keyboards import get_confirm_remind_creation_keyboard

from tasks import send_remind

TIME_FORMAT = '%d %B в %H:%M:%S'

router = Router()


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.new_group_remind))
async def new_group_remind_callback(callback: types.CallbackQuery, db_session: Session):
    groups = entities.user.get_user(db_session, callback.from_user.id).groups
    keyboard = keyboards.get_new_group_remind_keyboard(groups).as_markup()
    await callback.message.edit_text(texts.messages.new_group_remind, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.new_remind))
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


async def send_confirm_remind_creation(message: Message, state: FSMContext):
    # получаем ранее записанные данные
    data = await state.get_data()
    time_text = data["time"].strftime(TIME_FORMAT)
    await message.reply(
        "Почти готов, давай проверим, всё ли правильно?\n\n"
        f"Напоминание будет <b>{time_text}</b>\n"
        f"{data['text']}",
        reply_markup=get_confirm_remind_creation_keyboard()
    )

    # Переходим к состоянию "подтверждение создания"
    await state.set_state(states.CreateNewReminder.confirm_creation)


@router.message(states.CreateNewReminder.entering_time)
@router.message(states.CreateNewReminder.editing_time)
async def enter_remind_date(message: Message, state: FSMContext):
    time = message.text

    parsed_time = remind_parser.parse_time(time)
    if parsed_time is None:
        await message.reply("Неверный формат даты! Попробуйте ещё раз")
        return

    now = datetime.now()
    time_text = parsed_time.strftime(TIME_FORMAT)
    if parsed_time < now:
        await message.reply(f"Вы указали {time_text}\n"
                            "Нельзя указывать дату из прошлого. Введите другую дату")
        return

    await state.update_data(time=parsed_time)  # сохраняем введённую дату
    await state.update_data(entering_time=now)
    await send_confirm_remind_creation(message, state)


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.confirm_remind_creation))
async def confirm_remind_creation(
        callback: types.CallbackQuery,
        state: FSMContext, context: Context, db_session: Session):
    # Получаем контекст
    data = await state.get_data()

    # Считаем время напоминания с учётом времени отправки сообщения
    real_time: datetime = data['time'] + (datetime.now() - data['entering_time'])
    # Добавить напоминание в планировщик
    job = context.scheduler.add_job(send_remind, "date", run_date=real_time,
                            args=(callback.message.chat.id, data["text"]))

    # todo: добавить группу напоминания
    entities.remind.create_remind(db_session, callback.message.chat.id, real_time, data["text"], job.id)

    # todo: получение id группы напоминаний, если выбрана
    remind_group_id: Optional[int] = None
    if remind_group_id is not None:
        time_text = real_time.strftime(TIME_FORMAT)
        text = f'Создано новое групповое напоминание:\n' \
               f'{time_text},{data["text"]}'
        await send_message_to_remind_group(db_session, callback.bot, remind_group_id, text)

    # Отправить сообщение
    await callback.message.answer("☑️ Напоминание успешно создано")
    await callback.answer()


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.edit_remind_text))
async def edit_remind_text(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новый текст напоминания")
    await state.set_state(states.CreateNewReminder.editing_text)
    await callback.answer()


@router.message(states.CreateNewReminder.editing_text)
async def edit_remind_text(message: Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)  # Здесь мы сохраняем введенный текст
    await send_confirm_remind_creation(message, state)


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.edit_remind_time))
async def edit_remind_text(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новое время напоминания")
    await state.set_state(states.CreateNewReminder.editing_time)
    await callback.answer()


@router.message(F.text.lower().startswith("напомни"))
async def create_remind_from_text_handler(message: Message, state: FSMContext):
    prefix_len = len("напомни")
    text = message.text[prefix_len:].lstrip()
    parsed_time = remind_parser.parse_time(text)
    parsed_text = remind_parser.parse_text(text)
    await state.update_data(time=parsed_time, text=parsed_text )

    await send_confirm_remind_creation(message, state)