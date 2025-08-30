from sqlalchemy import Column, Integer, String, Enum, ForeignKey, UniqueConstraint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship, backref


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Models


class Folder(db.Model):
    __tablename__ = 'folders'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    parent_folder = Column(Integer, ForeignKey(column='folders.id'))
    # client = Column(Integer)
    children = relationship(
        "File", back_populates="parent"
        # , remote_side=[id]
    )
    parent = relationship('Folder', remote_side=[id])

    __table_args__ = (
        UniqueConstraint('parent_folder', 'name', name='uq_parent_name'),
    )

    def __init__(self, name, parent_folder, client):
        self.name = name
        self.parent_folder = parent_folder
        self.client = client

    def __repr__(self):
        return f'folder | name-{self.name}'


class File(db.Model):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    meta_data = Column(Integer, ForeignKey(column='meta_data.id'))
    parent_folder = Column(Integer, ForeignKey(column='folders.id'))
    parent = relationship("Folder", back_populates="children")


class Metadata(db.Model):
    __tablename__ = 'meta_data'
    id = Column(Integer, primary_key=True)
    # datanodes = relationship("Block", back_populates="metadata")


class Datanode(db.Model):
    __tablename__ = 'datanodes'
    id = Column(Integer, primary_key=True)


class Block(db.Model):
    __tablename__ = 'blocks'
    id = Column(Integer, primary_key=True)
