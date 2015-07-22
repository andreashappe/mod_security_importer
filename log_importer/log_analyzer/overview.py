""" just outputs a (formatted) dump of the original data """

import argparse
from log_importer.data.db_helper import setup_connection
from log_importer.data.objects import Incident

def output_details(incident, detail):
    """ outputs a single line (describing one incident) """
    print("%s %s:%s -> %s %s:%s%s: %s" % (\
            incident.timestamp.strftime("%Y/%m/%d %H:%M%S"),
            incident.source.ip, incident.source.port,
            incident.method, incident.destination.ip, incident.destination.port,
            incident.path, detail.incident_catalog.message))

def output_overview():
    """ just outputs a (formatted) dump of the original data """
    parser = argparse.ArgumentParser(\
                        description="Give an high-level overview of database.")
    parser.add_argument('database', help="Database to analyze")

    args = parser.parse_args()

    # open database
    session = setup_connection(create_db=False, path=args.database)

    # show all incidences
    for incident in session.query(Incident).all():
        for detail in incident.details:
            output_details(incident, detail)

    # close database
    session.close()
