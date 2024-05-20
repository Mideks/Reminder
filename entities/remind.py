from datetime import datetime
from typing import Optional, TYPE_CHECKING, Type

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.base import BaseScheduler
from sqlalchemy import Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship

from entities.base import Base

if TYPE_CHECKING:
    from .remind_group import RemindGroup
    from .user import User


class Remind(Base):
    __tablename__ = 'reminders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    user: Mapped[Optional["User"]] = relationship("User", back_populates="reminds")

    remind_group_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('remind_groups.id'), nullable=True)
    remind_group: Mapped[Optional["RemindGroup"]] = relationship("RemindGroup", back_populates="reminds")

    remind_date: Mapped[datetime] = mapped_column(DateTime)
    text: Mapped[str] = mapped_column(String)
    scheduler_job_id: Mapped[Optional[str]] = mapped_column(String)


def create_remind(session: Session, user_id: int, remind_date: datetime, text: str,
                  remind_group_id: Optional[int] = None, scheduler_job_id: Optional[str] = None) -> Remind:
    new_remind = Remind(
        user_id=user_id, remind_date=remind_date, text=text,
        scheduler_job_id=scheduler_job_id, remind_group_id=remind_group_id
    )
    session.add(new_remind)
    session.commit()
    return new_remind


def get_group_reminds(session: Session, remind_group_id: int) -> list[Type[Remind]]:
    raise NotImplementedError()


async def get_user_reminds(session: Session, user_id: int) -> list[Type[Remind]]:
    reminds = (session.query(Remind)
               .filter(Remind.user_id == user_id, Remind.remind_date > datetime.now())
               .order_by(Remind.remind_date).all())
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
