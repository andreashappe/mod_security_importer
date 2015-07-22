""" Tests data serialization of objects into the database yields
    uncorrupted data. """

import datetime

from log_importer.log_import.parser import parse_incident
from log_importer.log_import.reader import read_file
from log_importer.data.db_helper import setup_connection
from log_importer.data.objects import Incident

def common_data(i, incident):
    """ common tests that should hold in all cases. """
    assert i.fragment_id == '7cf8df3f'
    assert i.timestamp == datetime.datetime(2015, 3, 30, 21, 10, 38),\
            "timestamp is: %r" % incident.timestamp # should be in UTC
    assert i.unique_id == 'VRm7zgr5AlMAAClwIZoAAAAU'
    assert i.source.ip == '10.199.23.1'
    assert i.source.port == 40889
    assert i.destination.ip == '1.2.3.4'
    assert i.destination.port == 18060
    assert i.host == "somehostname.at",\
                    "unexpected host, was: %r" % incident.host
    assert i.path == "/fubar/sr/10/SomeAction.do",\
                    "invalid path, was:%r" %incident.path
    assert i.method == "GET",\
                    "unexpected HTTP method, was: %r" % incident.method

    expected_ids = sorted([960024, 981203])
    found_ids = sorted([x.incident_catalog.catalog_id for x in  i.details])
    assert found_ids == expected_ids

def test_import_without_parts():
    """ import file without saving (optional) parts. """

    result = read_file('log_importer/tests/test_files/file_read_test.txt')
    session = setup_connection(create_db=True)
    incident = parse_incident(session, result[0],\
                              result[1], include_parts=False)

    session.add(incident)
    session.commit()

    # reload from db
    i = session.query(Incident).filter(Incident.id == incident.id).first()

    common_data(i, incident)
    assert not i.parts

def test_import_with_parts():
    """ import file while saving (optional) parts. """

    result = read_file('log_importer/tests/test_files/file_read_test.txt')
    session = setup_connection(create_db=True)
    incident = parse_incident(session, result[0], result[1], include_parts=True)

    session.add(incident)
    session.commit()

    # reload from db
    i = session.query(Incident).filter(Incident.id == incident.id).first()

    common_data(i, incident)
    assert len(i.parts) == 6
