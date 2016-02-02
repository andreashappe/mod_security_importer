import argparse

from sqlalchemy import func, desc
from log_importer.data.db_helper import setup_connection
from log_importer.data.objects import IncidentCatalogEntry


def retrieve_data(session):
    """ gets raw output data from the database """
    return session.query(IncidentCatalogEntry).all()


def output_incident_types():
    """ group database by <ip, port and error-message>
        and output group error counts. """

    parser = argparse.ArgumentParser(\
                    description="List all known incident types.")
    parser.add_argument('database', help="Database to analyze")
    args = parser.parse_args()

    # open database
    session = setup_connection(create_db=False, path=args.database)

    # show the different catalog types
    for i in retrieve_data(session):
        print("id %3d: %s:%d %s" % (i.catalog_id, i.config_file, i.config_line, i.message))

    # close database
    session.close()
