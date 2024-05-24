import os
from pathlib import Path

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.orm import Session

import entities
import keyboards
import remind_parser
import texts
from callbacks import ActionButtonAction, ActionButton
from context import Context
from remind_parser.STT import STT
from helpers import get_confirm_creation_text, create_remind_from_data
from remind_parser.gpt import remind_summary
from states.state_data import StateData

stt = STT()

router = Router()


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.create_remind_from_voice))
async def create_remind_from_voice_callback(callback: types.CallbackQuery, state: FSMContext, state_data: StateData):
    await callback.message.edit_text(
        texts.messages.create_remind_from_voice,
        reply_markup=keyboards.get_create_remind_from_voice_keyboard().as_markup()
    )
    await callback.answer()


# Хэндлер на получение голосового и аудио сообщения
@router.message(F.content_type.in_({
    types.ContentType.VOICE,
    types.ContentType.AUDIO,
    types.ContentType.DOCUMENT
}), )
async def voice_message_handler(message: types.Message, state: FSMContext, state_data: StateData):
    """
    Обработчик на получение голосового и аудио сообщения.
    """
    if message.content_type == types.ContentType.VOICE:
        file_id = message.voice.file_id
    elif message.content_type == types.ContentType.AUDIO:
        file_id = message.audio.file_id
    elif message.content_type == types.ContentType.DOCUMENT:
        file_id = message.document.file_id
    else:
        await message.reply(texts.messages.format_not_supported)
        return

    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("temp", f"{file_id}.tmp")
    await message.bot.download_file(file_path, destination=file_on_disk)
    bot_message = await message.answer(texts.messages.audio_received)

    text = stt.audio_to_text(file_on_disk)
    if not text:
        text = texts.messages.format_not_supported
        await bot_message.edit_text(text)
        os.remove(file_on_disk)  # Удаление временного файла
        return

    await bot_message.edit_text(texts.messages.successful_recognition)
    summary = remind_summary(text)

    raw_reminds = []
    for line in summary.split("\n"):
        line = line.replace("напомни", "").strip()
        parsed_time = remind_parser.texts.parse_time(line)
        parsed_text = remind_parser.texts.parse_text(line)
        if parsed_time and parsed_text:
            raw_reminds.append([parsed_time, parsed_text, None])

    state_data.raw_reminds = raw_reminds

    await send_raw_remind_list(bot_message, state, state_data)

    os.remove(file_on_disk)  # Удаление временного файла


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.back_to_raw_remind_list))
async def send_raw_remind_list_callback(callback: types.CallbackQuery, state: FSMContext, state_data: StateData):
    await send_raw_remind_list(callback.message, state, state_data)
    await callback.answer()


async def send_raw_remind_list(message: Message, state: FSMContext, state_data: StateData):
    index = state_data.selected_raw_remind
    if index is not None:
        data = await state.get_data()
        state_data.raw_reminds[index][0] = data["time"]
        state_data.raw_reminds[index][1] = data["text"]
        state_data.raw_reminds[index][2] = state_data.selected_remind_group_id
        state_data.selected_raw_remind = None

    raw_reminds = state_data.raw_reminds
    await message.edit_text(
        texts.messages.parsed_reminds,
        reply_markup=keyboards.get_parsed_reminds_keyboard(raw_reminds).as_markup()
    )


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.edit_raw_remind))
async def edit_raw_remind_handler(callback: types.CallbackQuery, state: FSMContext, state_data: StateData, callback_data: ActionButton):
    index = int(callback_data.data)
    raw_remind = state_data.raw_reminds[index]
    state_data.selected_raw_remind = index
    await state.update_data(time=raw_remind[0], text=raw_remind[1])
    state_data.selected_remind_group_id = raw_remind[2]

    await callback.message.edit_text(
        await get_confirm_creation_text(state),
        reply_markup=keyboards.get_confirm_remind_creation_keyboard(True).as_markup()
    )


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.approve_all_reminds))
async def approve_all_reminds_handler(
        callback: types.CallbackQuery, context: Context,
        state_data: StateData, db_session: Session):
    raw_reminds = state_data.raw_reminds

    for time, text, group_id in raw_reminds:
        await create_remind_from_data(callback.message, context, db_session, time, text, group_id)

    await callback.message.edit_text(
        texts.messages.raw_remind_creation_successful,
        reply_markup=keyboards.get_navigation_keyboard(
            texts.buttons.back_to_menu, ActionButtonAction.show_menu
        ).as_markup()
    )


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.edit_remind_group_for_all_raw))
async def edit_remind_group_for_all_raw_callback(callback: types.CallbackQuery, db_session: Session):
    groups = entities.user.get_user(db_session, callback.from_user.id).groups
    keyboard = keyboards.get_edit_remind_group_for_all_raw_keyboard(groups).as_markup()
    await callback.message.edit_text(texts.messages.new_group_remind, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ActionButton.filter(F.action == ActionButtonAction.edit_group_for_all_raw_reminds))
async def edit_group_for_all_raw_reminds_callback(
        callback: types.CallbackQuery, state: FSMContext, state_data: StateData, callback_data: ActionButton):
    group_id = int(callback_data.data)
    for raw in state_data.raw_reminds:
        raw[2] = group_id

    await send_raw_remind_list(callback.message, state, state_data)
    await callback.answer(texts.messages.group_changed_successful_for_all_raws)
