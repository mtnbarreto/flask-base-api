# project/models/event_descriptor.py

from datetime import datetime
from project.extensions import db

class EventDescriptor(db.Model):
    __tablename__ = "event_descriptors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, id: int, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description