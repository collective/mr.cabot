from sqlalchemy import (
    Column,
    Date,
    Enum,
    ForeignKey,
    Float,
    Index,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Activity(Base):
    __tablename__ = 'activity'
    id = Column(Integer, primary_key=True)
    type = Column(Enum('commit', 'issue', 'email', 'question', 'answer', name="activity_types"))
    identity_id = Column(Integer, ForeignKey('identity.id'))
    identity = relationship("Identity", backref="activities")
    
    native_id = Column(Text)
    date = Column(Date)
    
    def __repr__(self):
        return "<%s object from %s at %s>" % (self.type, self.date, self.native_id)

class Contributor(Base):
    __tablename__ = 'contributor'
    id = Column(Integer, primary_key=True)
    display_name = Column(Text)

class Identity(Base):
    __tablename__ = 'identity'
    id = Column(Integer, primary_key=True)    
    uri = Column(Text)
    contributor_id = Column(Integer, ForeignKey('contributor.id'))
    contributor = relationship("Contributor",
        backref="identities")
    
    def __repr__(self):
        return "<mr.cabot.models.Identity object representing %s>" % (self.uri)

class ContributorLocation(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True)
    display_name = Column(Text)
    contributor_id = Column(Integer, ForeignKey('contributor.id'))
    contributor = relationship("Contributor",
        backref="locations")
    latitude = Column(Float)
    longitude = Column(Float)
    from_date = Column(Date)
    to_date = Column(Date)


Index('identity_uri', Identity.uri, unique=True, mysql_length=255)
Index('location_from', ContributorLocation.from_date)
Index('location_to', ContributorLocation.to_date)
Index('activity_native', Activity.native_id, unique=True)

