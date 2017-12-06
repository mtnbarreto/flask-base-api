# project/models/user_group_association.py

from datetime import datetime
from project import db
from project.models.user import User
from project.models.group import Group

class UserGroupAssociation(db.Model):
    __tablename__ = "user_group_associations"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), primary_key=True)
    user = db.relationship("User", back_populates="associated_groups")
    group = db.relationship("Group", back_populates="associated_users")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, user: User, group: Group):
        self.user = user
        self.group = group