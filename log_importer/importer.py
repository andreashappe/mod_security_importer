import argparse
import multiprocessing

from log_importer.log_import.parser import parse_incident
from log_importer.log_import.reader import read_from_file
from log_importer.data.db_helper import setup_connection
from log_importer.data.db_helper import get_or_create
from log_importer.data.objects import *

from multiprocessing import Pool, cpu_count


def forward_to_db(session, i):
    incident = Incident(fragment_id=i['fragment_id'],
                        timestamp=i['timestamp'],
                        unique_id=i['unique_id'],
                        destination=get_or_create(session, Destination,
                                                  ip=i['destination'][0],
                                                  port=i['destination'][1]),
                        source=get_or_create(session, Source,
                                                  ip=i['source'][0],
                                                  port=i['source'][1]),
                        host=i['host'],
                        method=i['method'],
                        path=i['path'],
                        http_code=i['http_code']
                        )
    for p in i['parts']:
        incident.parts.append(p)

    for p in i['details']:
        if 'msg' in p.keys():
            entry = get_or_create(session, IncidentCatalogEntry,
                                  message=p['msg'],
                                  config_file=p['file'],
                                  catalog_id=int(p['id']),
                                  config_line=int(p['line']))
            
            incident.details.append(IncidentDetail(incident_catalog=entry))

    session.add(incident)
    session.commit()

    return incident


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

    pool = Pool(processes=cpu_count())
    incidents = [pool.apply_async(parse_incident, args=(read_from_file(f), args.import_parts,)) for f in args.files]

    # write stuff to database
    output = [forward_to_db(session, p.get()) for p in incidents]

    # close database
    session.close()
