import argparse

from log_importer.data.db_helper import setup_connection
from log_importer.data.objects import Incident

def main():
    parser = argparse.ArgumentParser(description="Give an high-level overview of database.")
    parser.add_argument('database', help="Database to analyze")

    args = parser.parse_args()

    # open database
    session = setup_connection(create_db=False, path=args.database)

    # show all incidences
    for i in session.query(Incident).all():
        for m in i.details:
            print "%s %s:%s -> %s %s:%s%s: %s" % (i.timestamp.strftime("%Y/%m/%d %H:%M%S"), i.source.ip, i.source.port, i.method, i.destination.ip, i.destination.port, i.path, m.incident_catalog.message)

    # close database
    session.close()

main()
