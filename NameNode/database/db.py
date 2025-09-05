from sqlalchemy import Column, Integer, String, Enum, ForeignKey, UniqueConstraint, BigInteger, DateTime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship, backref
from datetime import datetime


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

    parent = relationship(
        "Folder",
        remote_side=[id],
        back_populates="children")
    children = relationship(
        "Folder", back_populates="parent", cascade="all, delete-orphan")
    files = relationship('File', back_populates='parent',
                         cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('parent_folder', 'name', name='uq_parent_name'),
    )

    def __init__(self, name, parent_folder):
        self.name = name
        self.parent_folder = parent_folder

    def get_path(self):
        parts = [self.name]
        folder: Folder = self.parent
        while folder:
            parts.append(folder.name)
            folder = folder.parent
        return "/".join(reversed(parts))

    def __repr__(self):
        return f'Folder: {self.name}'


class File(db.Model):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    size = Column(Integer)  # bytes
    created_at = Column(DateTime, default=datetime.now())
    parent_folder = Column(Integer, ForeignKey(
        column='folders.id', ondelete='CASCADE'))

    parent = relationship("Folder", back_populates="files")
    blocks = relationship('Block', back_populates='file',
                          cascade="all, delete-orphan")
    __table_args__ = (
        UniqueConstraint('parent_folder', 'name', name='uq_parent_name'),
    )

    def __init__(self, name, size, parent_folder):
        self.name = name
        self.size = size
        self.parent_folder = parent_folder

    def get_path(self):
        parts = [self.name]
        folder: Folder = self.parent
        while folder:
            parts.append(folder.name)
            folder = folder.parent
        return "/".join(reversed(parts))

    def __repr__(self):
        return f'File: {self.name}'


class Datanode(db.Model):
    __tablename__ = 'datanodes'
    id = Column(Integer, primary_key=True)
    ip = Column(String(50), nullable=False)
    port = Column(Integer, nullable=False)
    capacity = Column(BigInteger, default=0)  # capacidad total
    used = Column(BigInteger, default=0)  # espacio usado
    last_heartbeat = Column(DateTime, default=datetime.now())

    blocks = db.relationship(
        "Block", back_populates="datanode", cascade="all, delete-orphan")

    def __init__(self, ip, port, capacity):
        self.ip = ip
        self.port = port
        self.capacity = capacity


class Block(db.Model):
    __tablename__ = 'blocks'
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey(
        column='files.id', ondelete='CASCADE'))
    datanode_id = Column(Integer, ForeignKey(
        column='datanodes.id', ondelete='CASCADE'))
    part = Column(Integer)
    # size = Column(Integer)

    datanode = relationship("Datanode", back_populates='blocks')
    file = relationship('File', back_populates='blocks',)

    def __init__(self, file_id, datanode_id, part):
        self.file_id = file_id
        self.datanode_id = datanode_id
        self.part = part

    def __repr__(self):
        return f'{self.file.name}_part{self.part}.dat'
