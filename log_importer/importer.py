import argparse

from log_importer.log_import.parser import parse_incident
from log_importer.log_import.reader import read_from_file
from log_importer.data.db_helper import setup_connection

def import_log_to_database():
    parser = argparse.ArgumentParser(description="Import Log-Files into Database.")
    parser.add_argument('database', help="Database to import to")
    parser.add_argument('files', metavar='File', type=file, nargs='+')
    parser.add_argument('--import-parts', help="import raw parts", action="store_true")

    args = parser.parse_args()

    if args.import_parts:
        print "also adding parts!"
    else:
        print "not adding parts"

    # open database
    session = setup_connection(create_db=True, path=args.database)

    # add files
    for f in args.files:
        print "parsing " + f.name
        tmp = read_from_file(f)
        incident = parse_incident(session, tmp[0], tmp[1], include_parts=args.import_parts)

        print "adding " + f.name + " to db"
        session.add(incident)
        session.commit()

    # close database
    session.close()
