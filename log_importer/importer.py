import argparse

from log_importer.log_import.parser import parse_incident
from log_importer.log_import.reader import read_from_file
from log_importer.data.db_helper import setup_connection

from multiprocessing import Process, cpu_count, Queue


def import_worker(jobs, session, import_parts):

    f = jobs.get()
    while f is not None:
        print("parsing " + f.name)
        tmp = read_from_file(f)

        incident = parse_incident(session, tmp[0], tmp[1], include_parts=args.import_parts)

        print("adding " + f.name + " to db")
        session.add(incident)
        session.commit()

	f = jobs.get()


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

    # open database
    session = setup_connection(create_db=True, path=args.database)

    # WIP: add a minimal multiprocessing implementation
    jobs = Queue()
    workers = []
    num_workers = 1 # TODO: allow for multiple workers (db-depenedent)

    for w in range(num_workers):
        p = Process(target=import_worker, args=(jobs, session, args.import_parts))
        p.start()
        workers.append(p)

    # add files
    for f in args.files:
        jobs.put(f)

    # add stop bit
    for i in range(num_workers):
        jobs.put(None)

    # wait for workers to finish
    for p in workers:
        p.join()

    # close database
    session.close()
