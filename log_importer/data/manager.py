from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def get_base():
    return Base

def setup_connection(create_db=False, path=''):
    if len(path) > 0:
        engine = create_engine('sqlite:///' + path)
    else:
        engine = create_engine('sqlite://')
    session = sessionmaker()
    session.configure(bind=engine)

    if create_db:
        Base.metadata.create_all(engine)

    return session()
