""" tests if the string representation of an incident report can
    be transformed in a "real" python object representation.

    All test data from https://github.com/SpiderLabs/ModSecurity/wiki/ModSecurity-2-Data-Formats#Audit_Log_Header_code_classliteralAcode
    """

from log_importer.log_import.parser import parse_incident, parse_part_A,\
                                           parse_H_detail_message
from log_importer.log_import.reader import read_file
from log_importer.data.db_helper import setup_connection

import datetime

PART_A = "[09/Jan/2008:12:27:56 +0000] OSD4l1BEUOkAAHZ8Y3QAAAAH"\
         " 209.90.77.54 64995 80.68.80.233 80\r\n"

def test_parse_part_A():
    """ test if the right data was detected """

    result = parse_part_A(PART_A)

    assert result, "unexpected result %r" % result
    # time-parsing is a test-case on it's own
    assert result[1] == "OSD4l1BEUOkAAHZ8Y3QAAAAH"
    assert result[2] == "209.90.77.54"
    assert result[3] == 64995
    assert result[4] == "80.68.80.233"
    assert result[5] == 80

def test_parse_H_message():
    msg = "  [file \"/etc/httpd/modsecurity.d/owasp-modsecurity-crs/base_rules/modsecurity_crs_40_generic_attacks.conf\"] [line \"37\"] [id \"960024\"] [rev \"2\"] [msg \"Meta-Character Anomaly Detection Alert - Repetative Non-Word Characters\"] [data \"Matched Data: \xd0\x9c\xd0\xb8\xd0\xbd\xd0\xb8\xd1\x81\xd1\x82\xd0\xb0\xd1\x80\xd1\x81\xd1\x82\xd0\xb2\xd0\xbe \xd0\xb7\xd0\xb0 \xd0\xbe\xd0\xb1\xd1\x80\xd0\xb0\xd0\xb7\xd0\xbe\xd0\xb2\xd0\xb0\xd1\x9a\xd0\xb5 found within ARGS:keyword: \xd0\x9c\xd0\xb8\xd0\xbd\xd0\xb8\xd1\x81\xd1\x82\xd0\xb0\xd1\x80\xd1\x81\xd1\x82\xd0\xb2\xd0\xbe \xd0\xb7\xd0\xb0 \xd0\xbe\xd0\xb1\xd1\x80\xd0\xb0\xd0\xb7\xd0\xbe\xd0\xb2\xd0\xb0\xd1\x9a\xd0\xb5\"] [ver \"OWASP_CRS/2.2.8\"] [maturity \"9\"] [accuracy \"8\"] Warning. Pattern match \"\\\\W{4,}\" at ARGS:keyword.\""
    results = parse_H_detail_message(msg)

    assert results['id'] == "960024"
    assert results['line'] == "37"
    assert results['file'] == "/etc/httpd/modsecurity.d/owasp-modsecurity-crs/base_rules/modsecurity_crs_40_generic_attacks.conf"
    assert results['msg'] == "Meta-Character Anomaly Detection Alert - Repetative Non-Word Characters", "invalid msg, was: %r" % results["message"]
    
def test_parse_part_A_timestamp():
    """ test if the right data was detected """

    result = parse_part_A(PART_A)

    assert result[0] == datetime.datetime(2008, 1, 9, 12, 27, 56)

def test_parse_incident():
    result = read_file('log_importer/tests/test_files/file_read_test.txt')
    session = setup_connection(create_db=True)
    incident = parse_incident(session, result[0], result[1])

    assert incident.fragment_id == '7cf8df3f'
    assert incident.timestamp == datetime.datetime(2015, 3, 30, 21, 10, 38) # should be in UTC
    assert incident.unique_id == 'VRm7zgr5AlMAAClwIZoAAAAU'
    assert incident.source.ip == '10.199.23.1'
    assert incident.source.port == 40889
    assert incident.destination.ip == '1.2.3.4'
    assert incident.destination.port == 18060
    assert not incident.parts

def test_parse_incident_with_parts():
    result = read_file('log_importer/tests/test_files/file_read_test.txt')
    session = setup_connection(create_db=True)
    incident = parse_incident(session, result[0], result[1], include_parts=True)
    assert len(incident.parts) == 6

def test_parse_incident_with_B_record():
    result = read_file('log_importer/tests/test_files/file_read_test.txt')
    session = setup_connection(create_db=True)
    incident = parse_incident(session, result[0], result[1], include_parts=True)
    assert incident.host == "somehostname.at", "unexpected host, was: %r" % incident.host
    assert incident.path == "/fubar/sr/10/SomeAction.do", "invalid path, was:%r" %incident.path
    assert incident.method == "GET", "unexpected HTTP method, was: %r" % incident.method

def test_parse_incident_with_H_record():
    result = read_file('log_importer/tests/test_files/file_read_test.txt')
    session = setup_connection(create_db=True)
    incident = parse_incident(session, result[0], result[1], include_parts=True)

    expected_ids = sorted([960024, 981203])
    found_ids = sorted([i.incident_catalog.catalog_id for i in incident.details])

    assert found_ids == expected_ids
