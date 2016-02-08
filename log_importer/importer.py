import argparse
import multiprocessing
import sqlalchemy
import os,sys
import functools

from log_importer.log_import.parser import parse_incident
from log_importer.log_import.reader import read_from_file
from log_importer.data.db_helper import setup_connection
from log_importer.data.objects import *
from log_importer.cache import SourceCache, DestinationCache, IncidentDetailCache
from datetime import datetime
from concurrent import futures

from multiprocessing import Pool, cpu_count

class IncidentCount:
    def __init__(self, session):
        self.counter = retrieve_new_id_for(session, Incident)

    def getNext(self):
        self.counter += 1
        return self.counter

class IncidentCache:
    def __init__(self):
        self.incidentCache = []
        self.partCache = []

    def addIncident(self, incident):
        self.incidentCache.append(incident)

    def addPart(self, part):
        self.partCache.append(part)

    def getCount(self):
        return len(self.incidentCache)

    def writeParts(self, conn):
        if self.partCache:
            conn.execute(Part.__table__.insert().values(self.partCache))
        self.partCache = []

    def writeIncidents(self, conn):
        if self.incidentCache:
            conn.execute(Incident.__table__.insert().values(self.incidentCache))
        self.incidentCache = []

last = datetime.now()

def forward_to_db(session, i, id_counter, incident_cache, cache_destination, cache_source, cache_details, diff=1000):
    global last

    internal_id = id_counter.getNext()
    source_id = cache_source.get_id(i['source'][0], i['source'][1])
    destination_id = cache_destination.get_id(i['destination'][0], i['destination'][1])

    incident = { 'id': internal_id,
                       'fragment_id': i['fragment_id'],
                       'timestamp': i['timestamp'],
                       'unique_id': i['unique_id'],
                       'source_id': source_id,
                       'destination_id': destination_id,
                       'host': i['host'],
                       'method': i['method'],
                       'path': i['path'],
                       'http_code': i['http_code']
    }

    incident_cache.addIncident(incident)

    for p in i['parts']:
        p['incident_id'] = internal_id
        incident_cache.addPart(p)

    [ cache_details.add_detail(internal_id, p['msg'], p['file'], int(p['id']), int(p['line'])) for p in i['details'] if 'msg' in p.keys()]

    if incident_cache.getCount() % diff == 0:
        conn = session.connection()
        cache_source.sync_to_db(conn)
        cache_destination.sync_to_db(conn)

        incident_cache.writeIncidents(conn)
        incident_cache.writeParts(conn)
        cache_details.sync_to_db(conn)

        session.commit()
        if sys.version_info[0] > 2 or (sys.version_info[0] == 2 and sys.version_info[1] >= 7):
            tmp = (datetime.now() - last).total_seconds()/diff*1000.0
            print("timing: : " + str(tmp) + "ms/import")
            last = datetime.now()
    return incident

def retrieve_new_id_for(session, klass):
    tmp = session.query(sqlalchemy.func.max(klass.id)).first()[0]
    return 1 if tmp is None else tmp+1


def tmp(f, directory='./'):
    return parse_incident(read_from_file(open(os.path.join(directory, f), 'r')))


def import_log_to_database():
    parser = argparse.ArgumentParser(description="Import Log-Files into Database.")
    parser.add_argument('database', help="Database to import to")
    parser.add_argument('files', nargs='+')
    parser.add_argument('--import-parts', help="import raw parts", action="store_true")

    args = parser.parse_args()

    if args.import_parts:
        print("also adding parts!")
    else:
        print("not adding parts")

    # open database to calculate num_worker
    session = setup_connection(create_db=True, path=args.database)

    cache_destination = DestinationCache(session)
    cache_source = SourceCache(session)
    cache_details = IncidentDetailCache(session)
    incident_counter = IncidentCount(session)
    incident_cache = IncidentCache()

    # files = [args.files[0].name]*20000
    with futures.ProcessPoolExecutor(max_workers=max(1, cpu_count()-1)) as executor:
<<<<<<< e0144fe9d771a3bf4aa3cf2d7f29b87ed6c494b6
        for incident in executor.map(tmp, files):
            try:
                forward_to_db(session, incident, incident_counter, incident_cache, cache_destination, cache_source, cache_details)
            except KeyError as e:
                print("ERROR: key error {0}: {1}".format(e.errno, e.strerror))
=======
        for filename in args.files:
            if os.path.isdir(filename):
                for root, dirs, subfiles in os.walk(filename):
                    for incident in executor.map(functools.partial(tmp, directory=root), subfiles):
                        forward_to_db(session, incident, incident_counter, incident_cache, cache_destination, cache_source, cache_details)
            else:
                for incident in executor.map(tmp, [filename]):
                    forward_to_db(session, incident, incident_counter, incident_cache, cache_destination, cache_source, cache_details)
>>>>>>> initial directory support

    # close database
    conn = session.connection()
    cache_source.sync_to_db(conn)
    cache_destination.sync_to_db(conn)
    incident_cache.writeIncidents(conn)
    incident_cache.writeParts(conn)
    cache_details.sync_to_db(conn)
    session.commit()
    session.close()
