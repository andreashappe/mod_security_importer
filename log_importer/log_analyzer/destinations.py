import argparse

import log_importer
import log_importer.log_import

from log_importer.log_import.parser import parse_incident
from log_importer.log_import.reader import read_from_file
from log_importer.data.manager import setup_connection
from log_importer.data.objects import *

from sqlalchemy import func, desc

def main():
    parser = argparse.ArgumentParser(description="Give an high-level overview of database.")
    parser.add_argument('database', help="Database to analyze")

    args = parser.parse_args()

    # open database
    session = setup_connection(create_db=False, path=args.database)

    # show all incidences
    for ip, port, msg, cnt in session.query(Destination.ip, Destination.port, IncidentCatalogEntry.message, func.count(Destination.ip).label("count")).\
                                  filter(Incident.destination_id == Destination.id).\
                                  filter(IncidentDetail.incident_id == Incident.id).\
                                  filter(IncidentDetail.incident_catalog_id == IncidentCatalogEntry.id).\
                                  group_by(Destination.ip, Destination.port, IncidentCatalogEntry.message).\
                                  order_by(desc("count")).\
                                  all():
        print "%3d: %s:%5d %s" % (cnt, ip, port, msg)

    # close database
    session.close()

main()
