from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from log_importer.data.manager import get_base

Base = get_base()

class Destination(Base):
    __tablename__ = 'destinations'
    id = Column(Integer, primary_key=True)

    ip = Column(String)
    port = Column(Integer)

class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)

    ip = Column(String)
    port = Column(Integer)

class Incident(Base):
    __tablename__ = 'incidents'
    id = Column(Integer, primary_key=True)

    # extracted from 'A' record
    timestamp = Column(DateTime)
    fragment_id = Column(String)
    unique_id = Column(String)

    destination_id = Column(Integer, ForeignKey(Destination.id))
    destination    = relationship(Destination)

    source_id = Column(Integer, ForeignKey(Source.id))
    source    = relationship(Source)

    # (optional parts)
    parts = relationship("Part", backref="incident")

    # (optional incident_details)
    details = relationship("IncidentDetail", backref="incident")

    # extracted from 'B' record
    host = Column(String)
    method = Column(String)
    path = Column(String)

class IncidentCatalogEntry(Base):
    __tablename__ = 'incident_catalog_entries'
    id = Column(Integer, primary_key=True)

    catalog_id = Column(Integer)
    config_file = Column(String)
    config_line = Column(Integer)
    message = Column(String)

class IncidentDetail(Base):
    __tablename__ = 'incident_details'
    id = Column(Integer, primary_key=True)

    incident_id = Column(Integer, ForeignKey(Incident.id))

    incident_catalog_id = Column(Integer, ForeignKey(IncidentCatalogEntry.id))
    incident_catalog   = relationship(IncidentCatalogEntry)


class Part(Base):
    __tablename__ = 'parts'
    id = Column(Integer, primary_key=True)

    category = Column(String)
    body = Column(String)

    incident_id = Column(Integer, ForeignKey(Incident.id))
