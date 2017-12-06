# project/models/device.py

from datetime import datetime
from project import db
from project.models.user import User
from project.models.group import Group
from typing import List

class Device(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(128), unique=True, nullable=False)
    device_type = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    pn_token = db.Column(db.String(256), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('devices', lazy='joined'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, device_id: str, device_type: str, pn_token: str=None, active: bool=True, user=None, created_at: datetime=datetime.utcnow()):
        self.device_id = device_id
        self.device_type = device_type  # "apple" "android"
        self.pn_token = pn_token
        self.active = active
        self.user = user
        self.created_at = created_at
        self.updated_at = created_at

    # noinspection PyPep8
    @staticmethod
    def query_active_devices_for_user(user: User):
        return Device.query.filter(Device.user_id == user.id, Device.active == True, Device.pn_token.isnot(None))

    # noinspection PyPep8
    @staticmethod
    def query_active_devices_for_group(group: Group, discard_user_ids:List[int]=None):
        discard_user_ids = discard_user_ids or []
        user_ids = [user.user_id for user in group.associated_users if user.user_id not in discard_user_ids]
        return Device.query.filter(Device.user_id.in_(tuple(user_ids)), Device.active == True,
                                   Device.pn_token.isnot(None))

    @staticmethod
    def create_or_update(device_id, device_type: str, user:User=None, active: bool = True, pn_token: str=None):
        device = Device.first_by(device_id=device_id)
        if not device:
            device = Device(device_id=device_id, device_type=device_type, user=user, active=active, pn_token=pn_token)
            db.session.add(device)
        else:
            device.device_type = device_type
            device.active = active
            if user:
                device.user = user
            if pn_token:
                device.pn_token = pn_token
        return device

    @staticmethod
    def first_by(**kwargs):
        """Get first db device that match to device_id"""
        return Device.query.filter_by(**kwargs).first()

    @staticmethod
    def first(*criterion):
        """Get first db entity that match to criterium"""
        return Device.query.filter(*criterion)
