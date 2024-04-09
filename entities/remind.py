from datetime import datetime
from typing import Optional

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.base import BaseScheduler
from sqlalchemy import Integer, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, Session

from entities.base import Base


class Remind(Base):
    __tablename__ = 'reminders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    creation_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    remind_date: Mapped[datetime] = mapped_column(DateTime)
    title: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(String)
    scheduler_job_id: Mapped[str] = mapped_column(String)


async def get_user_reminds(session: Session, user_id: int):
    reminds = session.query(Remind).filter(Remind.user_id == user_id).order_by(Remind.remind_date).all()
    return reminds


def get_remind_by_id(session: Session, remind_id: int) -> Remind:
    return session.query(Remind).get(remind_id)


def delete_remind_by_id(session: Session, scheduler: BaseScheduler, remind_id: int) -> Remind:
    remind = get_remind_by_id(session, remind_id)
    try:
        scheduler.remove_job(remind.scheduler_job_id)
    except JobLookupError:
        print(f"Уведомление истекло ({remind.scheduler_job_id})")

    session.delete(remind)
    session.commit()

    return remind