from apscheduler.schedulers.base import BaseScheduler
from sqlalchemy.orm import Session, sessionmaker


class Context:
    db_session_maker: sessionmaker[Session]
    scheduler: BaseScheduler

    def __init__(self, db_session_maker: sessionmaker[Session], scheduler: BaseScheduler):
        self.db_session_maker = db_session_maker
        self.scheduler = scheduler
