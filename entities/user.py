from typing import List, TYPE_CHECKING

from sqlalchemy import Integer
from sqlalchemy.orm import relationship, mapped_column, Mapped, Session

from entities.base import Base

if TYPE_CHECKING:
    from entities.remind_group import RemindGroup
    from entities.remind import Remind


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Relationship to Remind
    reminds: Mapped[List['Remind']] = relationship("Remind", back_populates="user")

    # Relationship to Group
    groups: Mapped[List['RemindGroup']] = relationship("RemindGroup", secondary="user_remind_group",
                                                     back_populates="users")


def create_user_if_not_exists(session: Session, user_id: int) -> bool:
    user = session.query(User).get(user_id)
    if user:
        return False

    new_user = User(id=user_id)
    session.add(new_user)
    session.commit()
    return True
