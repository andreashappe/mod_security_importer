""" all objects that will be stored within the database.

    this currently triggers a lot of pylint errors which are mostly
    false positive and a pylint bug: http://www.logilab.org/ticket/33636
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from log_importer.data.db_helper import get_base

BASE = get_base()


class Destination(BASE):
    """ Destination IP+Port. """

    __tablename__ = 'destinations'
    id = Column(Integer, primary_key=True)

    ip = Column(String, index=True)
    port = Column(Integer, index=True)


class Source(BASE):
    """ Source IP+Port. Maybe we should merge this with Destination
        into a Host type"""

    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)

    ip = Column(String)
    port = Column(Integer)


class Incident(BASE):
    """ A single incident (host+destination+address) can contain
        multiple sub-incidents (IncidentDetails) """

    __tablename__ = 'incidents'
    id = Column(Integer, primary_key=True)

    # extracted from 'A' record
    timestamp = Column(DateTime)
    fragment_id = Column(String)
    unique_id = Column(String)
    http_code = Column(String)

    destination_id = Column(Integer, ForeignKey(Destination.id))
    destination = relationship(Destination)

    source_id = Column(Integer, ForeignKey(Source.id))
    source = relationship(Source)

    # (optional parts)
    parts = relationship("Part", backref="incident")

    # (optional incident_details)
    details = relationship("IncidentDetail", backref="incident")

    # extracted from 'B' record
    host = Column(String)
    method = Column(String)
    path = Column(String)


class IncidentCatalogEntry(BASE):
    """ This is used within mod_security error messages to uniquely
        identify the incident definition. Move into a own object
        to make queries perform faster (later on). """

    __tablename__ = 'incident_catalog_entries'
    id = Column(Integer, primary_key=True)

    catalog_id = Column(Integer)
    config_file = Column(String)
    config_line = Column(Integer)
    message = Column(String, index=True)


class IncidentDetail(BASE):
    """ An incident can contain multiple sub-incident (aka IncidentDetail).
        Those are mostly a reference to the specific incident definition
        within the IncidentCatalog. """

    __tablename__ = 'incident_details'
    id = Column(Integer, primary_key=True)

    incident_id = Column(Integer, ForeignKey(Incident.id))

    incident_catalog_id = Column(Integer, ForeignKey(IncidentCatalogEntry.id))
    incident_catalog = relationship(IncidentCatalogEntry)


class Part(BASE):
    """ Part can (optionally) store all data of the original incident
        report within the database. This might come in handy if the
        incident reports should be parsed later on. """

    __tablename__ = 'parts'
    id = Column(Integer, primary_key=True)

    category = Column(String)
    body = Column(String)

    incident_id = Column(Integer, ForeignKey(Incident.id))
