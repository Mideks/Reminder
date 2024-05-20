import entities.remind
from main import bot, db_session
from texts.messages import remind_notification, group_remind_notification


async def send_remind(remind_id: int) -> None:
    session = db_session()
    remind = entities.remind.get_remind_by_id(session, remind_id)

    if remind.remind_group:
        group = remind.remind_group
        message_text = group_remind_notification.format(
            group=group.name, id=group.id, text=remind.text, user=remind.user.first_name)
        await entities.remind_group.send_message_to_remind_group(
            session, bot, group.id, message_text)
    else:
        message_text = remind_notification.format(text=remind.text)
        await bot.send_message(remind.user_id, message_text)

    session.close()