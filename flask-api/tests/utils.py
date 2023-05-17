# project/tests/utils.py

import datetime

from project import app
from project.extensions import bcrypt, db
from project.models.user import User, UserRole
from project.models.device import Device
from project.models.group import Group
from project.models.user_group_association import UserGroupAssociation



def add_user(username: str, email: str, password: str, cellphone_number: str=None, cellphone_cc: str=None,
             created_at:datetime=datetime.datetime.utcnow(), roles:UserRole=UserRole.USER):
    user = User(username=username, email=email, password=password, cellphone_number=cellphone_number,
                cellphone_cc=cellphone_cc, created_at=created_at, roles=roles)
    db.session.add(user)
    db.session.commit()
    return user

def add_device(device_id: str, device_type: str, active: bool=True, pn_token: str=None, user: User=None, created_at: datetime=datetime.datetime.utcnow()):
    device = Device(device_id=device_id, device_type=device_type, pn_token=pn_token, active=active, user=user, created_at=created_at)
    db.session.add(device)
    db.session.commit()
    return device

def add_group(name: str):
    group = Group(name=name)
    db.session.add(group)
    db.session.commit()
    return group

def add_user_group_association(user: User, group: Group):
    user_group_association = UserGroupAssociation(user=user, group=group)
    db.session.add(user_group_association)
    db.session.commit()
    return user_group_association

def set_user_token_hash(user: User, token: str):
    user.token_hash = bcrypt.generate_password_hash(token, app.config.get('BCRYPT_LOG_ROUNDS')).decode()
    db.session.commit()
    return user

def set_user_email_token_hash(user: User, token: str):
    user.email_token_hash = bcrypt.generate_password_hash(token, app.config.get('BCRYPT_LOG_ROUNDS')).decode()
    db.session.commit()
    return user
