"""common database helpers used by other modules"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def get_base():
    return Base


def engine_from_path(path):
    if not path:
        engine = create_engine('sqlite://')
    elif "://" not in path:
        engine = create_engine('sqlite:///' + path)
    else:
        engine = create_engine(path)

    return engine


def setup_connection(create_db=False, path=''):
    """ creates a new sqlite database connection. If path is
        empty (or a empty string is given) an in-memory
        database is created. Path accepts any sqlalchemy
        connection string. """

    engine = engine_from_path(path)
    session = sessionmaker()
    session.configure(bind=engine)

    if create_db:
        Base.metadata.create_all(engine)

    return session()
