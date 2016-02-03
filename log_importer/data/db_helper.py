"""common database helpers used by other modules"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def get_base():
    return Base


def engine_from_path(path):
    if not path:
	print "creating in-memory"
        engine = create_engine('sqlite://')
    elif "://" not in path:
	print "creating from file"
        engine = create_engine('sqlite:///' + path)
    else:
	print "creating from db"
        engine = create_engine(path)

    print "return engine"
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
