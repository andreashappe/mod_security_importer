import argparse

from log_importer.log_import.parser import parse_incident
from log_importer.log_import.reader import read_from_file
from log_importer.data.db_helper import setup_connection

from multiprocessing import Process, cpu_count, Queue


def import_worker(jobs, database, import_parts):
    """have to open a new database connection as we're in a new process"""

    session = setup_connection(create_db=True, path=database)

    name = jobs.get()
    f = open(name, 'r')
    while f is not None:
        print("parsing " + f.name)
        tmp = read_from_file(f)

        incident = parse_incident(session, tmp[0], tmp[1], include_parts=import_parts)
        print("adding " + f.name + " to db")
        session.add(incident)
        session.commit()
        f = jobs.get()

    session.commit()
    session.close()


def import_log_to_database():
    parser = argparse.ArgumentParser(description="Import Log-Files into Database.")
    parser.add_argument('database', help="Database to import to")
    parser.add_argument('files', metavar='File', type=argparse.FileType('r'), nargs='+')
    parser.add_argument('--import-parts', help="import raw parts", action="store_true")

    args = parser.parse_args()

    if args.import_parts:
        print("also adding parts!")
    else:
        print("not adding parts")

    # open database to calculate num_worker
    session = setup_connection(create_db=True, path=args.database)

    # WIP: add a minimal multiprocessing implementation
    jobs = Queue()
    workers = []

    # only allow mulitple workers for postgres backend
    if session.connection().engine.name == 'postgresql':
    	num_workers = cpu_count()
    else:
        num_workers = 1

    for w in range(num_workers):
        p = Process(target=import_worker, args=(jobs, args.database, args.import_parts))
        p.start()
        workers.append(p)

    # add files
    for f in args.files:
        jobs.put(f.name)

    # add stop bit
    for i in range(num_workers):
        jobs.put(None)

    # wait for workers to finish
    for p in workers:
        p.join()

    # close database
    session.close()
