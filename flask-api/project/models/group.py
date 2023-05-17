# project/models/group.py

from datetime import datetime
from project.extensions import db
from sqlalchemy.ext.associationproxy import association_proxy

class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    associated_users = db.relationship("UserGroupAssociation", back_populates="group")
    users = association_proxy('associated_users', 'user')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def get(id: int):
        """Get db entity that match the id"""
        return Group.query.get(id)