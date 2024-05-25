from typing import List, Optional

from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column, Session

from entities.base import Base
from entities.remind import Remind
from entities.user import User
from entities.user_remind_group import Role, UserRemindGroup


class RemindGroup(Base):
    """
    Represents a group of reminders.

    Attributes:
        id (Mapped[int]): The unique identifier of the group.
        name (Mapped[str]): The name of the group.
        users (Mapped[List[User]]): A list of users associated with this group.
        reminds (Mapped[List[Remind]]): A list of reminders associated with this group.
    """
    __tablename__ = 'remind_groups'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    # Relationship to User through the association table
    users: Mapped[List['User']] = relationship("User", secondary="user_remind_group", back_populates="groups")

    # Relationship to Remind
    reminds: Mapped[List[Remind]] = relationship("Remind", back_populates="remind_group")


def get_remind_group(session: Session, group_id: int) -> Optional[RemindGroup]:
    return session.query(RemindGroup).get(group_id)


def get_user_role(session: Session, remind_group_id: int, user_id: int) -> Role:
    """
    Retrieves the role of a user within a specific reminder group.

    This function queries the database for a UserRemindGroup entry that matches the given user_id and remind_group_id.
    If such an entry exists, it returns the role associated with that entry. Otherwise, it raises a ValueError.

    :param session: The database session used for querying.
    :param remind_group_id: The identifier of the reminder group.
    :param user_id: The identifier of the user.
    :return: The role of the user within the reminder group (e.g., member, admin).
    :raises ValueError: If no UserRemindGroup entry matches the provided identifiers.
    """
    user_remind_group: Optional[UserRemindGroup] = (
        session.query(UserRemindGroup).filter(
            UserRemindGroup.user_id == user_id,
            UserRemindGroup.remind_group_id == remind_group_id
        ).one_or_none()
    )

    if user_remind_group:
        return user_remind_group.role
    else:
        # Raise an error if no matching entry was found, indicating the user does not exist in the group
        raise ValueError("User does not exist in this group")


def create_remind_group(session: Session, name: str, owner_id: int) -> RemindGroup:
    """
    Creates a new reminder group with the given name and owner.

    Parameters:
    :param session: The SQLAlchemy session to use for database operations.
    :param name: The name of the new reminder group.
    :param owner_id: The ID of the user who owns the group.

    :return: The newly created remind group.
    """
    new_group = RemindGroup(name=name)
    session.add(new_group)
    session.commit()
    remind_group_join_user(session, owner_id, new_group.id, Role.owner)
    return new_group


def delete_remind_group_by_id(session: Session, remind_group_id: int) -> bool:
    """
    Deletes a reminder group by its ID.

    :param session: The SQLAlchemy session to use for database operations.
    :param remind_group_id: The ID of the reminder group to delete.
    :return: if deletion was successful return True
    """
    group = get_remind_group(session, remind_group_id)
    if not group:
        return False

    session.query(Remind).filter(Remind.remind_group_id == remind_group_id).delete(synchronize_session=False)

    session.delete(group)
    session.commit()
    return True


def change_remind_group_name(session: Session, remind_group_id: int, new_name: str) -> None:
    """
    Changes the name of a reminder group by its ID.

    :param session: The SQLAlchemy session to use for database operations.
    :param remind_group_id: The ID of the reminder group to rename.
    :param new_name: The new name for the reminder group.
    """
    group = get_remind_group(session, remind_group_id)
    if group:
        group.name = new_name
        session.commit()


async def send_message_to_remind_group(
        session: Session, bot: Bot, remind_group_id: int, text: str, ignore_users: Optional[set[int]] = None) -> None:
    """
    Sends a message to all users in a reminder group.

    :param ignore_users: A set of user_id's that will be ignoring
    :param session: The SQLAlchemy session to use for database operations.
    :param bot: The aiogram Bot instance to send messages through.
    :param remind_group_id: The ID of the reminder group to send messages to.
    :param text: message text that will be sand to all group members
    """
    group = get_remind_group(session, remind_group_id)
    if group:
        for user in group.users:
            if ignore_users and user.id in ignore_users:
                continue
            await bot.send_message(user.id, text)


async def get_remind_group_join_link(bot: Bot, remind_group_id: int) -> str:
    """
    Creates a deep link for a bot that reminds users to join a group.

    :param bot: The aiogram Bot instance.
    :param remind_group_id: The ID of the group to join.

    :return: A deep link that can be used to start the bot with the specified payload.
    """
    # The payload includes the action ("join_group") and the group ID.
    payload = f"join_{remind_group_id}"
    return await create_start_link(bot, payload)


def remind_group_join_user(session: Session, user_id: int, remind_group_id: int, role: Role = Role.member) -> bool:
    """
    Adds a user to a reminder group with a specified role.

    Parameters:
    :param session: The SQLAlchemy session to use for database operations.
    :param user_id: The ID of the user to add to the group.
    :param remind_group_id: The ID of the reminder group to add the user to.
    :param role: The role of the user in the group. Defaults to Role.member.

    :return: If True - user successful added to group. False is already in group.
    """
    user: User = session.query(User).get(user_id)
    # Check if the user is not already in the specified remind group
    if not user:
        raise ValueError("User does not exists id database")
    if any(group.id == remind_group_id for group in user.groups):
        return False
    new_join = UserRemindGroup(user_id=user.id, remind_group_id=remind_group_id, role=role.name)
    session.add(new_join)
    session.commit()
    return True


def remind_group_kick_user(session: Session, remind_group_id: int, user_id: int) -> bool:
    """
    Removes a user from a reminder group.

    :param session: The SQLAlchemy session to use for database operations.
    :param user_id: The ID of the user to remove from the group.
    :param remind_group_id: The ID of the reminder group to remove the user from.

    :return: If user was in group return True, else return False
    """
    user: User = session.query(User).get(user_id)
    # Check if the user is in the specified remind group
    if not user:
        raise ValueError("User does not exists id database")

    if not any(group.id == remind_group_id for group in user.groups):
        return False

    session.query(UserRemindGroup).filter(
        UserRemindGroup.user_id == user.id,
        UserRemindGroup.remind_group_id == remind_group_id).delete()

    session.commit()
    return True
