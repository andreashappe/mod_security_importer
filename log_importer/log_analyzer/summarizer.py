import argparse

from sqlalchemy import func, desc
from log_importer.data.db_helper import setup_connection
from log_importer.data.objects import Destination, IncidentCatalogEntry,\
                                      IncidentDetail, Incident, Source


def retrieve_data(session):
    """ gets raw output data from the database """
    return session.query(Source.ip, Destination.ip, Destination.port,
                         Incident.path, Incident.method,
                         IncidentCatalogEntry.message,
                         func.count(Destination.ip).label("count"))\
                  .filter(Incident.destination_id == Destination.id)\
                  .filter(IncidentDetail.incident_id == Incident.id)\
                  .filter(IncidentDetail.incident_catalog_id == IncidentCatalogEntry.id)\
                  .group_by(Source.ip, Destination.ip, Destination.port, Incident.method, Incident.path, IncidentCatalogEntry.message)\
                  .order_by(desc("count"))\
                  .all()


def output_summary():
    parser = argparse.ArgumentParser(\
                    description="Give an high-level overview of database.")
    parser.add_argument('database', help="Database to analyze")

    args = parser.parse_args()

    # open database
    session = setup_connection(create_db=False, path=args.database)

    # show all incidences
    for source, ipaddress, port, path, method, msg, cnt in retrieve_data(session):
        print("%5d: %s -> %s %s:%5d%s %s" % (cnt, source, method, ipaddress, port, path, msg))

    # close database
    session.close()
