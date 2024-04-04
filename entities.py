from typing import Optional

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, DeclarativeBase
from sqlalchemy.sql.sqltypes import Integer
from datetime import datetime

class Base(DeclarativeBase):
    pass


class Remind(Base):
    __tablename__ = 'reminders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    creation_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    remind_date: Mapped[datetime] = mapped_column(DateTime)
    title: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(String)
    scheduler_job_id: Mapped[str] = mapped_column(String)
