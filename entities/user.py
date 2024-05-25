from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, mapped_column, Mapped, Session
from entities.base import Base

if TYPE_CHECKING:
    from entities.remind_group import RemindGroup
    from entities.remind import Remind



class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)

    # Relationship to Remind
    reminds: Mapped[List['Remind']] = relationship("Remind", back_populates="user")

    # Relationship to Group
    groups: Mapped[List['RemindGroup']] = relationship(
        "RemindGroup", secondary="user_remind_group", back_populates="users")


def update_user(session: Session, user_id: int, first_name: str, last_name: str) -> bool:
    """
    Updates the first name and last name of a user if they exist, otherwise creates a new user.

    :param session: The SQLAlchemy session object used for database operations.
    :param user_id: The ID of the user to update or create.
    :param first_name: The new first name for the user.
    :param last_name: The new last name for the user.

    :return: True if a user was successfully updated or created, False if the user was not found and thus not updated or created.
    """
    user = session.query(User).get(user_id)
    if user:
        # update user data
        user.first_name = first_name
        user.last_name = last_name
        session.commit()
        return False
    else:
        # if user not found create new
        new_user = User(id=user_id, first_name=first_name, last_name=last_name)
        session.add(new_user)
        session.commit()
        return True


def get_user(session: Session , user_id: id) -> User:
    return session.query(User).get(user_id)
