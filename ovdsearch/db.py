import logging

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.sql.expression import func

from datetime import datetime


Base = declarative_base()


log = logging.getLogger(__name__)


class Prisoner(Base):
    __tablename__ = "prisoners"
    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, index=True)
    description = Column(String)
    # найден ли политзэк или ещё неизвестно
    found = Column(Boolean, default=False, index=True)

    created = Column(DateTime)
    updated = Column(DateTime)

    def get_ovd_to_call(self, session):
        p2o = session.query(PrisonerToOVD.ovd_id).filter(
            PrisonerToOVD.prisoner_id == self.id
        )
        log.debug("Got p2o: %r", p2o)
        ovd = session.query(OVD).filter(~OVD.id.in_(p2o)).order_by(func.random()).first()
        return ovd


class OVD(Base):
    __tablename__ = "ovd"
    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=False, index=True)
    phones = Column(String, nullable=False)


# Соответствие юзеров и политзэков - кто кого ищет
class UserToPrisoner(Base):
    __tablename__ = "user2prisoner"
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, nullable=False, index=True)
    prisoner_id = Column(Integer, nullable=False, index=True)


# Соответствие зэков и ОВД - куда точно позвонили и где его точно нет
class PrisonerToOVD(Base):
    __tablename__ = "prisoner2ovd"
    id = Column(Integer, primary_key=True)

    prisoner_id = Column(Integer, nullable=False, index=True)
    ovd_id = Column(Integer, nullable=False, index=True)
    # статусы ОВД: not_present - позвонили в ОВД, там ответили, что зэка нет; no_answer - в ОВД не берут, other_problem - что-то еще не так.
    ovd_status = Column(String, default="not_present", index=True)


class Database:
    MEMORY = "sqlite:///:memory:"

    def __init__(self, url):
        self.engine = sqlalchemy.create_engine(url)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def new_session(self):
        return sqlalchemy.orm.Session(self.engine)

    def add_prisoner(self, name):
        prisoner = Prisoner(name=name)
        prisoner.created = datetime.now()
        prisoner.updated = datetime.now()
        session = self.new_session()
        session.add(prisoner)
        session.commit()

    def get_lost_prisoner(self):
        session = self.new_session()
        prisoner = (
            session.query(Prisoner)
            .filter(Prisoner.found == False)
            .order_by(func.random())
            .first()
        )
        return prisoner
