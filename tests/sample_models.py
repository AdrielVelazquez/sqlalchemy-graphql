from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker

from tests import R
engine = create_engine('sqlite:///:memory:', echo=True)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()


@R.ParentModel.CanBe
class ParentModel(Base):
    __tablename__ = "parents"
    id = Column(Integer, primary_key=True)
    name = Column(String)


@R.ChildModel.CanBe
class ChildModel(Base):
    __tablename__ = "children"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
    parent = relationship("ParentModel", backref=backref("children", lazy="dynamic", cascade="all,delete-orphan"))

Base.metadata.create_all()
