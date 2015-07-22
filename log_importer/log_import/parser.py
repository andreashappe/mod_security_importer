import re
import locale
import datetime

from string import split

# this is renamed to urllib.parse in python3
from urlparse import urlparse

from log_importer.data.objects import Incident, IncidentCatalogEntry, IncidentDetail, Source, Destination, Part
from log_importer.data.db_helper import get_or_create

def parse_part_A(part):
    matcher = re.match(r"^\[([^\]]+)\] ([^ ]+) ([^ ]+) ([^ ]+) ([^ ]+) ([^ ]+)\r\n$", part)
    assert matcher

    # time parsing is locale dependent. Assume that it is always the same
    # as on my desktop
    assert locale.getlocale() == (None, None)

    # manually convert timestamp into UTC. Python's strptime function cannot handle
    # +0000 (which is somehow not mentioned in the documentation). python-dateutil
    # cannot handle the custom mod_security timestamp format
    parts = matcher.group(1).split()
    time = datetime.datetime.strptime(parts[1], "+%H%M")
    timestamp = datetime.datetime.strptime(parts[0], "%d/%b/%Y:%H:%M:%S") - datetime.timedelta(hours=time.hour, minutes=time.minute)

    return (timestamp, matcher.group(2), matcher.group(3), int(matcher.group(4)), matcher.group(5), int(matcher.group(6)))

def parse_H_detail_message(msg):
    result = {}
    for i in [split(x, ' ', 1) for x in re.findall(r"\[([^\]]*)\]", msg)]:
        if len(i) == 2:
            key = i[0].strip()
            value = i[1].strip("\"")
            result[key] = value
    return result

def get_incident_catalog_entry_for(session, msg):
    parsed = parse_H_detail_message(msg)
    return get_or_create(session, IncidentCatalogEntry, message=parsed['msg'], config_file=parsed['file'], catalog_id=int(parsed['id']), config_line=int(parsed['line'] ))

def parse_part_H(session, part):

    messages = []

    for i in [split(x, ':', 1) for x in part]:
        if i[0] == "Message":
            messages.append(IncidentDetail(incident_catalog=get_incident_catalog_entry_for(session, i[1])))

    return messages

def parse_part_B(parts):
    # check if we start with GET/etc. Request
    matcher = re.match("^([^ ]+) (.*)\r\n$", parts[0])

    if matcher:
        method = matcher.group(1).strip()
        path = urlparse(matcher.group(2)).path

    for i in [split(x, ':', 1) for x in parts]:
        if i[0] == "Host":
            host = i[1].strip()

    return host, method, path

def parse_incident(session, fragment_id, parts, include_parts=False):

    # create the incident and fill it with data from the 'A' part
    assert 'A' in parts
    result_A = parse_part_A(parts['A'][0])
    incident = Incident(fragment_id = fragment_id,
                        timestamp = result_A[0],
                        unique_id = result_A[1],
                        destination = get_or_create(session, Destination, ip=result_A[4], port=result_A[5]),
                        source = get_or_create(session, Source, ip=result_A[2], port=result_A[3])
                       )
    # import parts
    if include_parts:
        for (cat, body) in parts.items():
            merged_part = "\n".join(body)
            incident.parts.append(Part(category=cat, body=merged_part))

    # import details from 'B' part (if exists)
    if 'B' in parts:
        incident.host, incident.method, incident.path = parse_part_B(parts['B'])

    # import details from 'H' part (if exists)
    if 'H' in parts:
        [incident.details.append(i) for i in parse_part_H(session, parts['H'])]

    return incident
