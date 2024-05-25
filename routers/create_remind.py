from datetime import datetime

from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.orm import Session

import entities
import keyboards
import remind_parser.texts
import states
from callbacks import ActionButton, ActionButtonAction
from context import Context
from helpers import get_confirm_creation_text, create_remind_from_data
from keyboards import get_confirm_remind_creation_keyboard
from states.state_data import StateData
import texts.messages
from texts.messages import TIME_FORMAT

router = Router()


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.new_group_remind))
async def new_group_remind_callback(callback: types.CallbackQuery, db_session: Session):
    groups = entities.user.get_user(db_session, callback.from_user.id).groups
    keyboard = keyboards.get_new_group_remind_keyboard(groups).as_markup()
    await callback.message.edit_text(texts.messages.new_group_remind, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.edit_remind_group))
async def edit_remind_group_callback(callback: types.CallbackQuery, db_session: Session):
    groups = entities.user.get_user(db_session, callback.from_user.id).groups
    keyboard = keyboards.get_edit_remind_group_keyboard(groups).as_markup()
    await callback.message.edit_text(texts.messages.new_group_remind, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.select_group_for_new_remind))
async def select_group_for_new_remind_handler(
        callback: types.CallbackQuery, state: FSMContext, callback_data: ActionButton,
        db_session: Session, state_data: StateData):
    group_id = int(callback_data.data)
    group = entities.remind_group.get_remind_group(db_session, group_id)
    state_data.selected_remind_group_id = group_id

    text = texts.messages.select_group_for_new_remind.format(name=group.name, id=group_id)
    await callback.message.edit_text(text)
    await state.set_state(states.states.CreateNewReminder.entering_text)
    await callback.answer()


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.edit_group_for_new_remind))
async def select_group_for_new_remind_handler(
        callback: types.CallbackQuery, state: FSMContext, callback_data: ActionButton, state_data: StateData):
    group_id = int(callback_data.data)
    state_data.selected_remind_group_id = group_id

    await send_confirm_remind_creation(callback.message, state)
    await callback.message.delete()
    await callback.answer()


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.new_remind))
async def enter_remind_creation(
        callback: types.CallbackQuery,
        state: FSMContext):
    await callback.message.edit_text(
        texts.messages.entering_remind_creation,
        reply_markup=keyboards.get_entering_remind_creation_keyboard().as_markup())
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


async def send_confirm_remind_creation(message: Message, state: FSMContext, state_data: StateData):
    raw = state_data.raw_reminds is not None
    await message.answer(
        await get_confirm_creation_text(state),
        reply_markup=get_confirm_remind_creation_keyboard(raw).as_markup()
    )

    # Переходим к состоянию "подтверждение создания"
    await state.set_state(states.states.CreateNewReminder.confirm_creation)


@router.message(states.states.CreateNewReminder.entering_time)
@router.message(states.states.CreateNewReminder.editing_time)
async def enter_remind_date(message: Message, state: FSMContext, state_data: StateData):
    time = message.text

    parsed_time = remind_parser.texts.parse_time(time)
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
    await send_confirm_remind_creation(message, state, state_data)


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.show_confirm_remind_creation_menu))
async def show_confirm_remind_creation_menu_handler(
        callback: types.CallbackQuery, state: FSMContext, state_data: StateData):
    await send_confirm_remind_creation(callback.message, state, state_data)


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.confirm_remind_creation))
async def confirm_remind_creation(
        callback: types.CallbackQuery, state_data: StateData,
        state: FSMContext, context: Context, db_session: Session):
    data = await state.get_data()
    await create_remind_from_data(
        callback.message, context, db_session, data['time'], data['text'],
        state_data.selected_remind_group_id, data.get("entering_time", None)
    )

    # Отправить сообщение
    await callback.message.edit_text(
        texts.messages.remind_creation_successful,
        reply_markup=keyboards.get_remind_creation_successful_keyboard().as_markup())
    await callback.answer()


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.edit_remind_text))
async def edit_remind_text(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(texts.messages.edit_remind_text)
    await state.set_state(states.states.CreateNewReminder.editing_text)
    await callback.answer()


@router.message(states.states.CreateNewReminder.editing_text)
async def edit_remind_text(message: Message, state: FSMContext, state_data: StateData):
    text = message.text
    await state.update_data(text=text)  # Здесь мы сохраняем введенный текст
    await send_confirm_remind_creation(message, state, state_data)


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.edit_remind_time))
async def edit_remind_text(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(texts.messages.edit_remind_time)
    await state.set_state(states.states.CreateNewReminder.editing_time)
    await callback.answer()


@router.message(F.text.lower().startswith("напомни"))
async def create_remind_from_text_handler(message: Message, state: FSMContext, state_data: StateData):
    prefix_len = len("напомни")
    text = message.text[prefix_len:].lstrip()
    parsed_time = remind_parser.texts.parse_time(text)
    parsed_text = remind_parser.texts.parse_text(text)
    await state.update_data(time=parsed_time, text=parsed_text)

    await send_confirm_remind_creation(message, state, state_data)
