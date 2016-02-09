""" Tests data serialization of objects into the database yields
    uncorrupted data. """

import sqlalchemy

from datetime import datetime

from log_importer.log_import.parser import parse_incident
from log_importer.log_import.reader import read_file
from log_importer.data.db_helper import setup_connection
from log_importer.data.objects import Incident, Source
from log_importer.importer import forward_to_db, IncidentCount, IncidentCache
from log_importer.cache import SourceCache, DestinationCache, IncidentDetailCache


counter = 0
last = datetime.now()

def common_data(i, incident):
    """ common tests that should hold in all cases. """
    assert i.fragment_id == '7cf8df3f'
    assert i.timestamp == datetime(2015, 3, 30, 21, 10, 38),\
            "timestamp is: %r" % incident.timestamp # should be in UTC
    assert i.unique_id == u'VRm7zgr5AlMAAClwIZoAAAAU'
    assert i.source.ip == u'10.199.23.1'
    assert i.source.port == 40889
    assert i.destination.ip == u'1.2.3.4'
    assert i.destination.port == 18060
    assert i.host == u"somehostname.at",\
                    "unexpected host, was: %r" % incident.host
    assert i.path == u"/fubar/sr/10/SomeAction.do",\
                    "invalid path, was:%r" % incident.path
    assert i.method == u"GET",\
                    "unexpected HTTP method, was: %r" % incident.method

    expected_ids = sorted([960024, 981203])
    found_ids = sorted([x.incident_catalog.catalog_id for x in  i.details])
    assert found_ids == expected_ids

def test_import_without_parts():
    """ import file without saving (optional) parts. """

    result = read_file('log_importer/tests/test_files/file_read_test.txt')
    session = setup_connection(True, "postgresql://modsec@localhost/modsec")

    cache_destination = DestinationCache(session)
    cache_source = SourceCache(session)
    cache_details = IncidentDetailCache(session)
    incident_counter = IncidentCount(session)
    incident_cache = IncidentCache()

    incident = parse_incident(result, include_parts=False)
    incidentObject = forward_to_db(session, incident, incident_counter, incident_cache, cache_destination, cache_source, cache_details, diff=1)

    # reload from db
    i = session.query(Incident).filter(Incident.id == incidentObject['id']).first()

    common_data(i, incident)
    assert not i.parts

def test_import_with_parts():
    """ import file while saving (optional) parts. """

    result = read_file('log_importer/tests/test_files/file_read_test.txt')
    session = setup_connection(True, "postgresql://modsec@localhost/modsec")

    cache_destination = DestinationCache(session)
    cache_source = SourceCache(session)
    cache_details = IncidentDetailCache(session)
    incident_counter = IncidentCount(session)
    incident_cache = IncidentCache()

    incident = parse_incident(result, include_parts=True)
    incidentObject = forward_to_db(session, incident, incident_counter, incident_cache, cache_destination, cache_source, cache_details, diff=1)

    # reload from db
    i = session.query(Incident).filter(Incident.id == incidentObject['id']).first()

    common_data(i, incident)
    assert len(i.parts) == 6
