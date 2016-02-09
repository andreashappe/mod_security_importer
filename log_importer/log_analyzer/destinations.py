""" group database by <ip, port and error-message>
    and output group error counts. """

import argparse

from sqlalchemy import func, desc
from log_importer.data.db_helper import setup_connection
from log_importer.data.objects import Destination, IncidentCatalogEntry,
                                      IncidentDetail, Incident


def retrieve_data(session):
    """ gets raw output data from the database """
    return session.query(Destination.ip, Destination.port,
                         IncidentCatalogEntry.message,
                         func.count(Destination.ip).label("count"))\
                  .filter(Incident.destination_id == Destination.id)\
                  .filter(IncidentDetail.incident_id == Incident.id)\
                  .filter(IncidentDetail.incident_catalog_id == IncidentCatalogEntry.id)\
                  .group_by(Destination.ip, Destination.port, IncidentCatalogEntry.message)\
                  .order_by(desc("count"))\
                  .all()


def output_destinations():
    """ group database by <ip, port and error-message>
        and output group error counts. """

    parser = argparse.ArgumentParser(\
                    description="Give an high-level overview of database.")
    parser.add_argument('database', help="Database to analyze")

    args = parser.parse_args()

    # open database
    session = setup_connection(create_db=False, path=args.database)

    # show all incidences
    for ipaddress, port, msg, cnt in retrieve_data(session):
        print("%3d: %s:%5d %s" % (cnt, ipaddress, port, msg))

    # close database
    session.close()
