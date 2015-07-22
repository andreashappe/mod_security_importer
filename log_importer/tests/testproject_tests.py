from nose.tools import *

import log_importer
from log_importer.data.objects import Destination
from log_importer.data.manager import setup_connection

def setup():
    print "SETUP!"

def teardown():
    print "TEAR DOWN!"

def test_basic():
    print "I RAN!"

def test_create_inmemory_db():
    setup_connection(create_db=True)

def test_insert_and_query():
    s = setup_connection(create_db=True)

    e = Destination(ip='127.0.0.1', port=80)
    s.add(e)
    s.commit()

    result = s.query(Destination).filter(Destination.ip == '127.0.0.1').all()
    print result

    s.close()
