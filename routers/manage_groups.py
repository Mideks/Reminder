import re

from aiogram import Router, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import entities.remind_group
import states
import texts.messages
from context import Context
from states import CreateReminderGroup

router = Router()


@router.message(Command('group_create'))
async def start_group_create_command(message: Message, state: FSMContext):
    await message.answer(texts.messages.create_group_enter_name)
    await state.set_state(CreateReminderGroup.entering_name)


@router.message(states.CreateReminderGroup.entering_name)
async def group_create_entering_name_handler(message: Message, context: Context):
    session = context.db_session_maker()
    name = message.text
    owner_id = message.from_user.id
    group = entities.remind_group.create_remind_group(session, name, owner_id)
    join_link = await entities.remind_group.get_remind_group_join_link(message.bot, group.id)

    text = texts.messages.create_group_success.format(link=join_link)
    await message.answer(text)


@router.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'join_(\d+)'))
))
async def join_group_command(message: Message, command: CommandObject, context: Context):
    remind_group_id = int(command.args.split("_")[1])
    user_id = message.from_user.id
    result = entities.remind_group.remind_group_join_user(context.db_session_maker(), user_id, remind_group_id)
    if result:
        await message.answer(f"Будем считать что вы теперь в группе #{remind_group_id}")
    else:
        await message.answer(f"Вы уже в группе #{remind_group_id}. Ливните.")


@router.message(Command('group_sending'))
async def group_sending_command(message: Message, command: CommandObject, context: Context):
    group_id, text = command.args.replace(" ", "_", 1).split("_")
    if group_id and text:
        await entities.remind_group.send_message_to_remind_group(
            context.db_session_maker(), message.bot, int(group_id), text
        )


