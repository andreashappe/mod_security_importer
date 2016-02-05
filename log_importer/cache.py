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


def retrieve_new_id_for(session, klass):
    tmp = session.query(sqlalchemy.func.max(klass.id)).first()[0]
    return 1 if tmp is None else tmp+1


class SourceCache:

    def __init__(self, session):
        self.session = session
        self.journal = {}
        self.tmp_id = retrieve_new_id_for(session, Source)

    def get_id(self, ip, port):
        key = ip + "-" + str(port)
        if key not in self.journal:
            tmp = self.session.query(Source.id).filter_by(ip=ip).filter_by(port=port).first()
            if tmp is None:
                self.tmp_id += 1
                self.journal[key] = {'id': self.tmp_id, 'ip': ip, 'port': port}
                return self.tmp_id
            return tmp[0]
        return self.journal[key]['id']

    def sync_to_db(self, conn):
        if self.journal:
            conn.execute(Source.__table__.insert().values(self.journal.values()))
        self.journal = {}

class DestinationCache:

    def __init__(self, session):
        self.cache = {}
        self.journal = []
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

    def __init__(self, session):
        self.session = session
        self.tmp_id = retrieve_new_id_for(session, Destination)
        self.cache = {}
        self.journal = []
        self.journal_details = []

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
