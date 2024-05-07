from typing import List, TYPE_CHECKING

from sqlalchemy import Integer
from sqlalchemy.orm import relationship, mapped_column, Mapped

from entities.base import Base
from entities.remind import Remind

if TYPE_CHECKING:
    from .remind_group import RemindGroup


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Relationship to Remind
    reminds: Mapped[List[Remind]] = relationship("Remind", back_populates="user")

    # Relationship to Group
    groups: Mapped[List['RemindGroup']] = relationship("RemindGroup", secondary="user_remind_group",
                                                     back_populates="users")
