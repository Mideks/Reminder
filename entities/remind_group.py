# todo: сделать сущеность группы и функции по работе с ней
from typing import List

from aiogram import Bot
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column, Session

from entities.base import Base
from entities.remind import Remind
from entities.user import User
from entities.user_remind_group import Role


class RemindGroup(Base):
    __tablename__ = 'remind_groups'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    # Relationship to User through the association table
    users: Mapped[List[User]] = relationship("User", secondary="user_remind_group", back_populates="remind_groups")

    # Relationship to Remind
    reminds: Mapped[List[Remind]] = relationship("Remind", back_populates="remind_group")


def create_remind_group(session: Session, name: str, owner_id: int) -> RemindGroup:
    pass


def delete_remind_group_by_id(session: Session, remind_group_id: int) -> None:
    pass


def change_remind_group_name(session: Session,  remind_group_id: int, new_name: str) -> None:
    pass


async def send_message_to_remind_group(session: Session, bot: Bot, remind_group_id: int, text: str) -> None:
    remind_group: RemindGroup = session.query(RemindGroup).get(remind_group_id)

    for user in remind_group.users:
        await bot.send_message(user.id, text)


def get_remind_group_join_link(session: Session, remind_group_id: int) -> str:
    pass


def remind_group_join_user(session: Session, user_id: int, role: Role = Role.member) -> None:
    pass


def remind_group_kick_user(session: Session, user_id: int) -> None:
    pass

