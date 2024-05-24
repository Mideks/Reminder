from datetime import datetime
from typing import Optional

from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.orm import Session

import entities
import texts.messages
from context import Context
from entities.remind_group import send_message_to_remind_group
from tasks import send_remind
from texts.messages import TIME_FORMAT


async def get_confirm_creation_text(state: FSMContext) -> str:
    data = await state.get_data()
    time_text = data["time"].strftime(TIME_FORMAT)
    text = data['text']
    return texts.messages.confirm_remind_creation.format(text=text, time_text=time_text)


async def create_remind_from_data(
        message: Message, context: Context,
        db_session: Session, time: datetime, text: str,
        remind_group_id: Optional[int] = None, entering_time: Optional[datetime] = None):
    real_time = time
    # Считаем время напоминания с учётом времени отправки сообщения
    if entering_time:
        real_time += datetime.now() - entering_time
    # Добавить напоминание в планировщик
    remind_text = text
    remind_group = entities.remind_group.get_remind_group(db_session, remind_group_id)

    if remind_group_id is not None:
        time_text = real_time.strftime(TIME_FORMAT)
        notification_text = texts.messages.group_remind_created_notification.format(
            time_text=time_text, text=remind_text, id=remind_group_id,
            name=remind_group.name, user=message.from_user.first_name)
        await send_message_to_remind_group(db_session, message.bot, remind_group_id, notification_text)

    remind = entities.remind.create_remind(
        db_session, message.chat.id, real_time, remind_text, remind_group_id)

    job = context.scheduler.add_job(
        send_remind, "date", run_date=real_time, args=(remind.id,))

    remind.scheduler_job_id = job.id
    db_session.add(remind)
    db_session.commit()
