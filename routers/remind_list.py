from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.base import BaseScheduler
from sqlalchemy.orm import Session, sessionmaker

import callbacks
from callbacks import ActionButton, RemindButton, RemindButtonAction
from context import Context
from entities.remind import get_user_reminds, get_remind_by_id, delete_remind_by_id
from keyboards import get_remind_list_keyboard, get_remind_menu_markup

router = Router()


# todo: добавить выбор группы, по которой смотрим напоминания
async def send_remind_list(message: Message, db_session: Session):
    user_id = message.chat.id
    text = "Вот ваш список ближайших напоминаний:\n\n"

    limit = 10
    reminds = (await get_user_reminds(db_session, user_id))[:limit]
    for i, remind in enumerate(reminds, 1):
        str_date = remind.remind_date.strftime('%d %B в %H:%M:%S')
        text += (f"<b>{i}. </b>{str_date}\n"
                 f"{remind.text}\n")

    text += "\nНажмите на кнопку ниже чтобы управлять напоминанием"

    if len(reminds) == 0:
        text = "У вас нет никаких напоминаний"

    await message.edit_text(text, reply_markup=get_remind_list_keyboard(reminds).as_markup())


@router.callback_query(ActionButton.filter(F.action == callbacks.ActionButtonAction.remind_list))
@router.callback_query(callbacks.NavigateButton.filter(F.location == callbacks.NavigateButtonLocation.remind_list))
async def send_remind_list_handler(callback: CallbackQuery, db_session: Session):
    await send_remind_list(callback.message, db_session)
    await callback.answer()


@router.callback_query(RemindButton.filter(F.action == callbacks.RemindButtonAction.show))
async def send_remind_menu(
        callback: CallbackQuery, callback_data: RemindButton, db_session: Session):
    remind = get_remind_by_id(db_session, callback_data.remind_id)
    str_date = remind.remind_date.strftime('%d %B в %H:%M:%S')
    text = (f"Напоминание на <b>{str_date}</b>\n\n"
            f"{remind.text}")

    await callback.message.edit_text(text, reply_markup=get_remind_menu_markup(remind).as_markup())
    await callback.answer()


@router.callback_query(RemindButton.filter(F.action == callbacks.RemindButtonAction.delete))
async def delete_remind(
        callback: CallbackQuery, callback_data: RemindButton, context: Context, db_session: Session):
    _ = delete_remind_by_id(db_session, context.scheduler, callback_data.remind_id)
    await callback.answer("Напоминание было удалено")
    await send_remind_list(callback.message, db_session)


# todo: добавить редактирование времени напоминания
# todo: добавить редактирование текста напоминания
# todo: отправка уведомления об изменении всем в группе (если есть)


