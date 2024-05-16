import re

from aiogram import Router, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import callbacks
import entities.remind_group
import entities.user
import keyboards
import states
import texts.messages
from context import Context
from entities.user_remind_group import Role
from states import CreateReminderGroup

router = Router()


@router.message(Command('group_create'))
async def start_group_create_command(message: Message, state: FSMContext):
    await message.answer(texts.messages.create_group_enter_name)
    await state.set_state(CreateReminderGroup.entering_name)


@router.message(states.CreateReminderGroup.entering_name)
async def group_create_entering_name_handler(message: Message, context: Context, state: FSMContext):
    session = context.db_session_maker()
    name = message.text
    owner_id = message.from_user.id
    group = entities.remind_group.create_remind_group(session, name, owner_id)
    join_link = await entities.remind_group.get_remind_group_join_link(message.bot, group.id)

    text = texts.messages.create_group_success.format(link=join_link)
    await message.answer(text)
    await state.clear()


@router.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'join_(\d+)'))
))
async def join_group_command(message: Message, command: CommandObject, context: Context):
    remind_group_id = int(command.args.split("_")[1])
    user_id = message.from_user.id
    result = entities.remind_group.remind_group_join_user(context.db_session_maker(), user_id, remind_group_id)
    if result:
        await message.answer(texts.messages.user_joined_to_group.format(remind_group_id=remind_group_id))
    else:
        await message.answer(texts.messages.user_already_in_group.format(remind_group_id=remind_group_id))


@router.message(Command('group_sending'))
async def group_sending_command(message: Message, command: CommandObject, context: Context):
    group_id, text = command.args.replace(" ", "_", 1).split("_")
    if group_id and text:
        await entities.remind_group.send_message_to_remind_group(
            context.db_session_maker(), message.bot, int(group_id), text
        )


@router.callback_query(callbacks.ActionButton.filter(F.action == callbacks.ActionButtonAction.show_group_list))
async def group_list_callback(callback: CallbackQuery, context: Context):
    await group_list_command(callback.message, context)
    await callback.answer()


@router.message(Command('groups'))
async def group_list_command(message: Message, context: Context):
    user_id = message.chat.id
    groups = entities.user.get_user(context.db_session_maker(), user_id).groups
    kb = keyboards.get_groups_list_keyboard(groups)
    await message.answer(texts.messages.show_groups_list, reply_markup=kb.as_markup())


@router.callback_query(callbacks.ActionButton.filter(F.action == callbacks.ActionButtonAction.show_group))
async def show_group_callback(
        callback: CallbackQuery, callback_data: callbacks.ActionButton, context: Context):
    group_id = int(callback_data.data)
    group_link = await entities.remind_group.get_remind_group_join_link(callback.bot, group_id)
    session = context.db_session_maker()
    group = entities.remind_group.get_remind_group(session, group_id)

    text = texts.messages.group_management.format(name=group.name, id=group_id, link=group_link)
    role = entities.remind_group.get_user_role(session, group_id, callback.message.chat.id)
    is_owner = role == Role.owner
    await callback.message.answer(text,
                                  reply_markup=keyboards.get_grop_management_keyboard(group, is_owner).as_markup())
    await callback.answer()


@router.callback_query(callbacks.ActionButton.filter((F.action == callbacks.ActionButtonAction.delete_remind_group)))
async def delete_remind_group_callback(callback: CallbackQuery, callback_data: callbacks.ActionButton, context: Context):
    group_id = int(callback_data.data)
    session = context.db_session_maker()
    group = entities.remind_group.get_remind_group(session, group_id)

    if group:
        await callback.message.answer(
            texts.messages.delete_remind_group_success.format(name=group.name, id=group_id))
        text = texts.messages.delete_remind_group_notification.format(name=group.name, id=group_id)
        await entities.remind_group.send_message_to_remind_group(session, callback.bot, group_id, text)

        entities.remind_group.delete_remind_group_by_id(session, group_id)
        await callback.answer()
    else:
        await callback.answer(texts.messages.delete_remind_group_fail)

