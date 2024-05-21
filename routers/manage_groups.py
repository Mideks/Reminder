import re

from aiogram import Router, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import Session

import callbacks
import entities.remind_group
import entities.user
import keyboards
import states
import texts.messages
from context import Context
from entities.user_remind_group import Role
from states.states import CreateReminderGroup

router = Router()


@router.message(Command('group_create'))
async def start_group_create_command(message: Message, state: FSMContext):
    await message.answer(texts.messages.create_group_enter_name)
    await state.set_state(CreateReminderGroup.entering_name)


@router.message(states.states.CreateReminderGroup.entering_name)
async def group_create_entering_name_handler(message: Message, context: Context, state: FSMContext, db_session: Session):
    name = message.text
    owner_id = message.from_user.id
    group = entities.remind_group.create_remind_group(db_session, name, owner_id)
    join_link = await entities.remind_group.get_remind_group_join_link(message.bot, group.id)

    text = texts.messages.create_group_success.format(link=join_link)
    await message.answer(text)
    await state.clear()


@router.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'join_(\d+)'))
))
async def join_group_command(message: Message, command: CommandObject, db_session: Session):
    remind_group_id = int(command.args.split("_")[1])
    user = message.from_user
    entities.user.update_user(db_session, user.id, user.first_name, user.last_name)

    group = entities.remind_group.get_remind_group(db_session, remind_group_id)
    db_user = entities.user.get_user(db_session, user.id)
    result = entities.remind_group.remind_group_join_user(db_session, user.id, remind_group_id)
    if result:
        await message.answer(texts.messages.user_joined_to_group.format(name=group.name, id=remind_group_id))
        text = texts.messages.user_join_to_remind_group_notification.format(
            user_name=db_user.first_name, group_name=group.name, group_id=remind_group_id)
        await entities.remind_group.send_message_to_remind_group(db_session, message.bot, remind_group_id, text,
                                                                 {user.id})
    else:
        await message.answer(texts.messages.user_already_in_group.format(name=group.name, id=remind_group_id))


@router.message(Command('group_sending'))
async def group_sending_command(message: Message, command: CommandObject, context: Context, db_session: Session):
    group_id, text = command.args.replace(" ", "_", 1).split("_")
    if group_id and text:
        await entities.remind_group.send_message_to_remind_group(
            db_session, message.bot, int(group_id), text
        )


@router.callback_query(callbacks.ActionButton.filter(F.action == callbacks.ActionButtonAction.show_group_list))
async def group_list_callback(callback: CallbackQuery, db_session: Session):
    await group_list_command(callback.message, db_session)
    await callback.answer()


@router.callback_query(callbacks.ActionButton.filter(F.action == callbacks.ActionButtonAction.show_remind_groups_list))
async def group_list_callback(callback: CallbackQuery, db_session: Session):
    await group_list_command(callback.message, db_session)
    await callback.answer()


@router.message(Command('groups'))
async def group_list_command(message: Message, db_session: Session):
    user_id = message.chat.id
    groups = entities.user.get_user(db_session, user_id).groups
    kb = keyboards.get_groups_list_keyboard(groups, callbacks.ActionButtonAction.show_group)
    await message.edit_text(texts.messages.show_groups_list, reply_markup=kb.as_markup())


@router.callback_query(callbacks.ActionButton.filter(F.action == callbacks.ActionButtonAction.show_group))
async def show_group_callback(
        callback: CallbackQuery, callback_data: callbacks.ActionButton, db_session: Session):
    group_id = int(callback_data.data)
    group_link = await entities.remind_group.get_remind_group_join_link(callback.bot, group_id)
    group = entities.remind_group.get_remind_group(db_session, group_id)

    text = texts.messages.group_management.format(name=group.name, id=group_id, link=group_link)
    role = entities.remind_group.get_user_role(db_session, group_id, callback.message.chat.id)
    is_owner = role == Role.owner
    keyboard = keyboards.get_grop_management_keyboard(group, is_owner).as_markup()
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(callbacks.ActionButton.filter((F.action == callbacks.ActionButtonAction.delete_remind_group)))
async def delete_remind_group_callback(callback: CallbackQuery, callback_data: callbacks.ActionButton, db_session: Session):
    group_id = int(callback_data.data)
    group = entities.remind_group.get_remind_group(db_session, group_id)

    if group:
        await callback.message.answer(
            texts.messages.delete_remind_group_success.format(name=group.name, id=group_id))
        text = texts.messages.delete_remind_group_notification.format(name=group.name, id=group_id)
        await entities.remind_group.send_message_to_remind_group(db_session, callback.bot, group_id, text)

        entities.remind_group.delete_remind_group_by_id(db_session, group_id)
        await callback.answer()
    else:
        await callback.answer(texts.messages.delete_remind_group_fail)


@router.callback_query(
    callbacks.ActionButton.filter((F.action == callbacks.ActionButtonAction.leave_from_remind_group)))
async def leave_from_remind_group_callback(
        callback: CallbackQuery, callback_data: callbacks.ActionButton, db_session: Session):
    group_id = int(callback_data.data)
    group = entities.remind_group.get_remind_group(db_session, group_id)
    user_id = callback.from_user.id
    user = entities.user.get_user(db_session, user_id)

    if group:
        kicked = entities.remind_group.remind_group_kick_user(db_session, group_id, user_id)
        if kicked:
            await callback.message.answer(texts.messages.leave_from_remind_group.format(
                id=group_id, name=group.name))
            text = texts.messages.leave_from_remind_group_notification.format(
                user_name=user.first_name, group_name=group.name, group_id=group_id)
            await entities.remind_group.send_message_to_remind_group(db_session, callback.bot, group_id, text)
            await callback.answer()
        else:
            await callback.answer(texts.messages.leave_from_remind_group_fail)
    else:
        await callback.answer(texts.messages.remind_group_does_not_exists_error)
