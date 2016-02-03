""" This module converts the string representation of an incident into
    a python (or rather sqlalchemy) object. """

# urllib.parse in python2/3
from future.standard_library import install_aliases
install_aliases()

import re
import datetime

from urllib.parse import urlparse
from log_importer.data.objects import Part

REGEXP_PART_A = '^\[([^\]]+)\] ([^ ]+) ([^ ]+) ([^ ]+) ([^ ]+) ([^ ]+)\n$'


def date_parser(match_group):
    """ manually convert timestamp into UTC. Python's strptime function cannot
        handle +0000 (which is somehow not mentioned in the documentation).
        python-dateutil cannot handle the custom mod_security timestamp format
    """

    parts = match_group.split()
    time = datetime.datetime.strptime(parts[1], "+%H%M")
    return datetime.datetime.strptime(parts[0], "%d/%b/%Y:%H:%M:%S") -\
                datetime.timedelta(hours=time.hour, minutes=time.minute)


def parse_part_A(part):
    """ Part A contains timestamp, id, destination and source information """

    matcher = re.match(REGEXP_PART_A, part)
    assert matcher

    timestamp = date_parser(matcher.group(1))

    return (timestamp, matcher.group(2),
            matcher.group(3), int(matcher.group(4)),
            matcher.group(5), int(matcher.group(6)))


def parse_H_detail_message(msg):
    result = {}
    for i in [x.split(' ', 1) for x in re.findall(r"\[([^\]]*)\]", msg)]:
        if len(i) == 2:
            key = i[0].strip()
            value = i[1].strip("\"")
            result[key] = value
    return result


def parse_part_H(part):

    messages = []

    for i in [x.split(':', 1) for x in part]:
        if i[0] == "Message":
            messages.append(parse_H_detail_message(i[1]))
    return messages


def parse_part_B(parts):
    # check if we start with GET/etc. Request
    matcher = re.match(r'^([^ ]+) (.*)\n$', parts[0])

    if matcher:
        method = matcher.group(1).strip()
        path = urlparse(matcher.group(2)).path
    else:
        method = None
        path = None

    for i in [x.split(':', 1) for x in parts]:
        if i[0] == "Host":
            host = i[1].strip()

    return host, method, path

def parse_incident(stuff, include_parts=False):

    """ takes (string) parts of an incident and converts those into
        a coherent python dictionary """

    fragment_id = stuff[0]
    parts = stuff[1]


    # create the incident and fill it with data from the 'A' part
    assert 'A' in parts
    result_A = parse_part_A(parts['A'][0])
    incident = { 'fragment_id': fragment_id,
                 'timestamp': result_A[0],
                 'unique_id': result_A[1],
                 'destination': [result_A[4], result_A[5]],
                 'source': [result_A[2], result_A[3]],
                 'parts': []
    }

    # import parts
    if include_parts:
        for (cat, body) in parts.items():
            merged_part = "\n".join(body)
            incident['parts'].append(Part(category=cat, body=merged_part))

    # import details from 'B' part (if exists)
    if 'B' in parts:
        incident['host'], incident['method'], incident['path'] = parse_part_B(parts['B'])
    else:
        incident['host'] = incident['method'] = incident['path'] = ""

    # import details from 'H' part (if exists)
    if 'H' in parts:
        incident['details'] = parse_part_H(parts['H'])
    else:
        incident['details'] = ''

    if 'F' in parts:
        incident['http_code'] = parts['F'][0].strip()
    else:
        incident['http_code'] = ''

    return incident
