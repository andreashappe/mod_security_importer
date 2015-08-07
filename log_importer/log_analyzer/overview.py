""" just outputs a (formatted) dump of the original data """

import argparse
from log_importer.data.db_helper import setup_connection
from log_importer.data.objects import Incident, Source, Destination

def output_details(incident, detail):
    """ outputs a single line (describing one incident) """
    print("%s %s %s:%s -> %s %s:%s%s: %s" % (\
            incident.timestamp.strftime("%Y/%m/%d %H:%M%S"),
            incident.unique_id,
            incident.source.ip, incident.source.port,
            incident.method, incident.destination.ip, incident.destination.port,
            incident.path, detail.incident_catalog.message))

def output_overview():
    """ just outputs a (formatted) dump of the original data """
    parser = argparse.ArgumentParser(\
                        description="Give an high-level overview of database.")
    parser.add_argument('database', help="Database to analyze")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--sort-by-time", action="store_true")
    group.add_argument("-s", "--sort-by-source-ip", action="store_true")
    group.add_argument("-d", "--sort-by-destination-ip", action="store_true")

    args = parser.parse_args()

    # open database
    session = setup_connection(create_db=False, path=args.database)

    # get results
    results = session.query(Incident)

    if args.sort_by_source_ip:
        results = results.join(Incident.source).order_by(Source.ip, Source.port).all()
    elif args.sort_by_destination_ip:
        results = results.join(Incident.destination).order_by(Destination.ip, Destination.port).all()
    else:
        results = results.order_by(Incident.timestamp).all()

    # show all incidences
    for incident in results:
        for detail in incident.details:
            output_details(incident, detail)

    # close database
    session.close()
