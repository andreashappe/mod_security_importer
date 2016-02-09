import argparse

from log_importer.data.db_helper import setup_connection

def create_database():
    parser = argparse.ArgumentParser(description="Create Database.")
    parser.add_argument('database', help="Database to import to")

    args = parser.parse_args()

    session = setup_connection(create_db=True, path=args.database)

    session.connection()
    session.close()
