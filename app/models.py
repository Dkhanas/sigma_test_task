from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

from db import engine, SessionLocal

Base = declarative_base()


class Pool(Base):
    __tablename__ = 'pools'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    domains = Column(JSON)

    @classmethod
    def load_pools(cls):
        initial_domain_pools = {}
        pools = SessionLocal().query(cls).all()

        for pool in pools:
            initial_domain_pools[str(pool.id)] = pool.domains
        return initial_domain_pools


class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    level = Column(String)
    request_form = Column(String)
    redirect_to = Column(String)
    status_code = Column(String)
    message = Column(String)


Base.metadata.create_all(bind=engine)
