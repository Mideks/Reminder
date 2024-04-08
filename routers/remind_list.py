from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.orm import Session, sessionmaker

import callbacks
from callbacks import ActionButton
from entities.remind import get_user_reminds, get_remind_by_id
from keyboards import get_remind_list_keyboard

router = Router()


@router.callback_query(ActionButton.filter(F.action == "remind_list"))
async def send_remind_list(callback: CallbackQuery, db_session: sessionmaker[Session]):
    text = "Вот ваш список ближайших напоминаний:\n\n"
    user_id = callback.message.chat.id

    with db_session() as session:
        limit = 10
        reminds = (await get_user_reminds(session, user_id))[:limit]
        for i, remind in enumerate(reminds, 1):
            str_date = remind.remind_date.strftime('%d %B в %H:%M:%S')
            text += (f"<b>{i}. </b>{str_date}\n"
                     f"{remind.text}\n")

        text += "\nНажмите на кнопку ниже чтобы управлять напоминанием"

        await callback.message.reply(text, reply_markup=get_remind_list_keyboard(reminds).as_markup())
        await callback.answer()






