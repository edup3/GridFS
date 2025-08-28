from sqlalchemy import Column, Integer, String, Enum, ForeignKey, UniqueConstraint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship, backref


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Models


class Node(db.Model):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    node_type = Column(Enum("file", "folder"))
    parent_node = Column(Integer, ForeignKey(column='nodes.id'))
    client = Column(Integer)
    children = relationship("Node", back_populates="parent", remote_side=[id])
    meta_data = Column(Integer, ForeignKey(column='meta_data.id'))

    __table_args__ = (
        UniqueConstraint('parent_node', 'name', name='uq_parent_name'),
    )

    def __init__(self, name, node_type, parent_node, client):
        self.name = name
        self.node_type = node_type
        self.parent_node = parent_node
        self.client = client

    def __repr__(self):
        return f'type-{self.node_type} | name-{self.name}'


class Metadata(db.Model):
    __tablename__ = 'meta_data'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
