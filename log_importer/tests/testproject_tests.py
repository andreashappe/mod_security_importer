from log_importer.data.objects import Destination
from log_importer.data.db_helper import setup_connection

def test_create_inmemory_db():
    """ a simple in-memory database-initialization should work """
    setup_connection(create_db=True)

def test_insert_and_query():
    """ data commited to the database should be readable afterwards"""
    session = setup_connection(create_db=True)

    destination = Destination(ip='127.0.0.1', port=80)
    session.add(destination)
    session.commit()

    result = session.query(Destination).filter(Destination.ip == '127.0.0.1').all()

    assert result[0].ip == destination.ip

    session.close()
