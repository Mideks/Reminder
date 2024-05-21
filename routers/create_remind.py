from datetime import datetime
from typing import Optional

from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.orm import Session

import entities
import keyboards
import remind_parser
import states
from callbacks import ActionButton, ActionButtonAction
from context import Context
from entities.remind_group import send_message_to_remind_group
from keyboards import get_confirm_remind_creation_keyboard
from states.state_data import StateData
from tasks import send_remind
import texts.messages

TIME_FORMAT = '%d %B в %H:%M:%S'

router = Router()


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.new_group_remind))
async def new_group_remind_callback(callback: types.CallbackQuery, db_session: Session):
    groups = entities.user.get_user(db_session, callback.from_user.id).groups
    keyboard = keyboards.get_new_group_remind_keyboard(groups).as_markup()
    await callback.message.edit_text(texts.messages.new_group_remind, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.select_group_for_new_remind))
async def select_group_for_new_remind_handler(
        callback: types.CallbackQuery, state: FSMContext, callback_data: ActionButton,
        db_session: Session, state_data: StateData):
    group_id = int(callback_data.data)
    group = entities.remind_group.get_remind_group(db_session, group_id)
    text = texts.messages.select_group_for_new_remind.format(name=group.name, id=group_id)
    state_data.selected_remind_group_id = group_id

    await callback.message.edit_text(text)
    await state.set_state(states.states.CreateNewReminder.entering_text)
    await callback.answer()


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.new_remind))
async def enter_remind_creation(
        callback: types.CallbackQuery, callback_data: ActionButton,
        state: FSMContext):
    await callback.message.edit_text(texts.messages.entering_remind_text)
    # Переходим к состоянию "ожидаю ввода текста напоминания"
    await state.set_state(states.states.CreateNewReminder.entering_text)
    await callback.answer()  # чтобы кнопка не зависала


@router.message(states.states.CreateNewReminder.entering_text)
async def enter_remind_text(message: Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)  # Здесь мы сохраняем введенный текст

    await message.reply(texts.messages.entering_remind_time)
    # Переходим к состоянию "ожидаю ввода времени напоминания"
    await state.set_state(states.states.CreateNewReminder.entering_time)


async def send_confirm_remind_creation(message: Message, state: FSMContext):
    # получаем ранее записанные данные
    data = await state.get_data()
    time_text = data["time"].strftime(TIME_FORMAT)
    text = data['text']
    await message.reply(
        texts.messages.confirm_remind_creation.format(text=text, time_text=time_text),
        reply_markup=get_confirm_remind_creation_keyboard()
    )

    # Переходим к состоянию "подтверждение создания"
    await state.set_state(states.states.CreateNewReminder.confirm_creation)


@router.message(states.states.CreateNewReminder.entering_time)
@router.message(states.states.CreateNewReminder.editing_time)
async def enter_remind_date(message: Message, state: FSMContext):
    time = message.text

    parsed_time = remind_parser.parse_time(time)
    if parsed_time is None:
        await message.answer(texts.messages.data_parse_error)
        return

    now = datetime.now()
    time_text = parsed_time.strftime(TIME_FORMAT)
    if parsed_time < now:
        await message.answer(texts.messages.time_from_past_error.format(time_text=time_text))
        return

    await state.update_data(time=parsed_time)  # сохраняем введённую дату
    await state.update_data(entering_time=now)
    await send_confirm_remind_creation(message, state)


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.confirm_remind_creation))
async def confirm_remind_creation(
        callback: types.CallbackQuery, state_data: StateData,
        state: FSMContext, context: Context, db_session: Session):
    # Получаем контекст
    data = await state.get_data()

    # Считаем время напоминания с учётом времени отправки сообщения
    real_time: datetime = data['time'] + (datetime.now() - data['entering_time'])
    # Добавить напоминание в планировщик
    remind_text = data["text"]

    remind_group_id: Optional[int] = state_data.selected_remind_group_id
    remind_group = entities.remind_group.get_remind_group(db_session, remind_group_id)

    if remind_group_id is not None:
        time_text = real_time.strftime(TIME_FORMAT)
        notification_text = texts.messages.group_remind_created_notification.format(
            time_text=time_text, text=remind_text, id=remind_group_id,
            name=remind_group.name, user=callback.from_user.first_name)
        await send_message_to_remind_group(db_session, callback.bot, remind_group_id, notification_text)

    remind = entities.remind.create_remind(
        db_session, callback.message.chat.id, real_time, remind_text, remind_group_id)

    job = context.scheduler.add_job(
        send_remind, "date", run_date=real_time, args=(remind.id,))

    remind.scheduler_job_id = job.id
    db_session.add(remind)
    db_session.commit()

    # Отправить сообщение
    await callback.message.edit_text(texts.messages.remind_creation_successful)
    await callback.answer()


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.edit_remind_text))
async def edit_remind_text(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(texts.messages.edit_remind_text)
    await state.set_state(states.states.CreateNewReminder.editing_text)
    await callback.answer()


@router.message(states.states.CreateNewReminder.editing_text)
async def edit_remind_text(message: Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)  # Здесь мы сохраняем введенный текст
    await send_confirm_remind_creation(message, state)


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.edit_remind_time))
async def edit_remind_text(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(texts.messages.edit_remind_time)
    await state.set_state(states.states.CreateNewReminder.editing_time)
    await callback.answer()


@router.message(F.text.lower().startswith("напомни"))
async def create_remind_from_text_handler(message: Message, state: FSMContext):
    prefix_len = len("напомни")
    text = message.text[prefix_len:].lstrip()
    parsed_time = remind_parser.parse_time(text)
    parsed_text = remind_parser.parse_text(text)
    await state.update_data(time=parsed_time, text=parsed_text)

    await send_confirm_remind_creation(message, state)
