import argparse
import multiprocessing
import sqlalchemy

from log_importer.log_import.parser import parse_incident
from log_importer.log_import.reader import read_from_file
from log_importer.data.db_helper import setup_connection
from log_importer.data.objects import *
from datetime import datetime
from concurrent import futures

from multiprocessing import Pool, cpu_count


counter = 0
last = datetime.now()
internal_id = 0

class SourceCache:

    tmp_id = None
    session = None
    journal = []

    def __init__(self, session):
        self.session = session
        self.tmp_id = retrieve_new_id_for(session, Source)

    def get_id(self, ip, port):
        tmp = self.session.query(Source.id).filter_by(ip=ip).filter_by(port=port).first()
        if tmp is None:
            self.tmp_id += 1
            self.journal.append({'id': self.tmp_id, 'ip': ip, 'port': port})
            return self.tmp_id
        else:
            return tmp[0]

    def sync_to_db(self, conn):
        if self.journal:
            conn.execute(Source.__table__.insert().values(self.journal))
        self.journal = []

class DestinationCache:
    tmp_id = None
    cache = {}
    session = None
    journal = []

    def __init__(self, session):
        self.session = session
        self.tmp_id = retrieve_new_id_for(session, Destination)

    def get_id(self, ip, port):
        key = ip + "-" + str(port)
        if key not in self.cache:
            tmp = self.session.query(Destination.id).filter_by(ip=ip).filter_by(port=port).first()
            if tmp is None:
                self.tmp_id += 1
                self.journal.append({'id': self.tmp_id, 'ip': ip, 'port': port})
                tmp = self.tmp_id 
            else:
                tmp = tmp[0]
            self.cache[key] = tmp
        return self.cache[key]

    def sync_to_db(self, conn):
        if self.journal:
            conn.execute(Destination.__table__.insert().values(self.journal))
        self.journal = []


class IncidentDetailCache:
    tmp_id = None
    cache = {}
    session = None
    journal = []
    journal_details = []

    def __init__(self, session):
        self.session = session
        self.tmp_id = retrieve_new_id_for(session, Destination)

    def add_detail(self, incident_id, message, cfile, key, line):
        if key not in self.cache:
            tmp = self.session.query(IncidentCatalogEntry.id).filter_by(catalog_id=key).first()
            if tmp is None:
                self.tmp_id += 1
                self.journal.append({'id': self.tmp_id, 'message': message, 'config_file': cfile, 'catalog_id': key, 'config_line': line})
                tmp = self.tmp_id 
            else:
                tmp = tmp[0]
            self.cache[key] = tmp
        ice_id = self.cache[key]
        self.journal_details.append({'incident_id': incident_id, 'incident_catalog_id': ice_id})

    def sync_to_db(self, conn):
        if self.journal:
            conn.execute(IncidentCatalogEntry.__table__.insert().values(self.journal))
        self.journal = []

        if self.journal_details:
            conn.execute(IncidentDetail.__table__.insert().values(self.journal_details))
        self.journal_details = []


incident_categories = []
incidents=[]

cache_destination = None
cache_source = None
cache_details = None

def forward_to_db(session, i):
    global counter
    global last
    global internal_id

    global incident_categories, incidents
    global cache_destination, cache_source, cache_details

    source_id = cache_source.get_id(i['source'][0], i['source'][1])
    destination_id = cache_destination.get_id(i['destination'][0], i['destination'][1])

    incidents.append({ 'id': internal_id,
                       'fragment_id': i['fragment_id'],
                       'timestamp': i['timestamp'],
                       'unique_id': i['unique_id'],
                       'source_id': source_id,
                       'destination_id': destination_id,
                       'host': i['host'],
                       'method': i['method'],
                       'path': i['path'],
                       'http_code': i['http_code']
    })

    for p in i['parts']:
        p['id'] = internal_id
        incident_categories += p

    [ cache_details.add_detail(internal_id, p['msg'], p['file'], int(p['id']), int(p['line'])) for p in i['details'] if 'msg' in p.keys()]

    diff = 1000
    counter += 1

    if counter % diff == 0:
        conn = session.connection()
        cache_source.sync_to_db(conn)
        cache_destination.sync_to_db(conn)
        if incident_categories:
            conn.execute(Part.__table__.insert().values(incident_categories))
        if incidents:
            conn.execute(Incident.__table__.insert().values(incidents))
        cache_details.sync_to_db(conn)

        incident_categories = []
        incidents = []

    	session.commit()
	tmp = (datetime.now() - last).total_seconds()/diff*1000.0
        print "counter " + str(counter) + ": " + str(tmp) + "ms/import"
	last = datetime.now()

    internal_id += 1


def retrieve_new_id_for(session, klass):
    tmp = session.query(sqlalchemy.func.max(klass.id)).first()[0]
    return 1 if tmp is None else tmp+1


def tmp(f):
    return parse_incident(read_from_file(open(f, 'r')))


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
    global internal_id, incidents, incident_categories
    global cache_destination, cache_source, cache_details

    session = setup_connection(create_db=True, path=args.database)

    cache_destination = DestinationCache(session)
    cache_source = SourceCache(session)
    cache_details = IncidentDetailCache(session)

    internal_id = retrieve_new_id_for(session, Incident)

    files = [args.files[0].name]*20000
    with futures.ProcessPoolExecutor(max_workers=max(1, cpu_count()-1)) as executor:
        for incident in executor.map(tmp, files):
            forward_to_db(session, incident)

    # close database
    conn = session.connection()
    cache_source.sync_to_db(conn)
    cache_destination.sync_to_db(conn)
    if incident_categories:
        conn.execute(Part.__table__.insert().values(incident_categories))
    if incidents:
        conn.execute(Incident.__table__.insert().values(incidents))
    cache_details.sync_to_db(conn)

    incident_categories = []
    incidents = []

    session.commit()
    session.close()
