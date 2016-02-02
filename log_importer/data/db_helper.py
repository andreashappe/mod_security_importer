"""common database helpers used by other modules"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def get_base():
    return Base


def setup_connection(create_db=False, path=''):
    """ creates a new sqlite database connection. If path is
        empty (or a empty string is given) an in-memory
        database is created """

    if len(path) > 0:
        engine = create_engine('sqlite:///' + path)
    else:
        engine = create_engine('sqlite://')
    session = sessionmaker()
    session.configure(bind=engine)

    if create_db:
        Base.metadata.create_all(engine)

    return session()


def get_or_create(session, model, **kwargs):
    """ analogous to ActiveRecord's find_or_create_by: test for
        existence of a record by some given fields. If it does
        not exist, create a new record"""
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance
