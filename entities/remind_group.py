# todo: сделать сущеность группы и функции по работе с ней
from typing import List

from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from entities.base import Base
from entities.remind import Remind
from entities.user import User


class RemindGroup(Base):
    __tablename__ = 'remind_groups'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    # Relationship to User through the association table
    users: Mapped[List[User]] = relationship("User", secondary="user_remind_group", back_populates="remind_groups")

    # Relationship to Remind
    reminds: Mapped[List[Remind]] = relationship("Remind", back_populates="remind_group")
