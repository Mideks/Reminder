import enum

from sqlalchemy import Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from entities.base import Base
from entities.remind_group import RemindGroup
from entities.user import User


class Role(enum.Enum):
    member = "member"
    admin = "admin"
    owner = "owner"


class UserRemindGroupAssociation(Base):
    __tablename__ = 'user_remind_group'

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
    user: Mapped[User] = relationship("User", back_populates="user_remind_group")

    remind_group_id: Mapped[int] = mapped_column(Integer, ForeignKey('remind_groups.id'), primary_key=True)
    remind_group: Mapped[RemindGroup] = relationship("RemindGroup", back_populates="user_remind_group")

    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.member)
