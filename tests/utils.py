# project/tests/utils.py

import datetime

from project import db, app
from project.models.models import User, Device, UserRole, Group, UserGroupAssociation
from project import bcrypt


def add_user(username, email, password, cellphone_number=None, cellphone_cc=None,
             created_at=datetime.datetime.utcnow(), roles=UserRole.USER):
    user = User(username=username, email=email, password=password, cellphone_number=cellphone_number,
                cellphone_cc=cellphone_cc, created_at=created_at, roles=roles)
    db.session.add(user)
    db.session.commit()
    return user

def add_device(device_id, device_type, active=True, pn_token=None, user=None, created_at=datetime.datetime.utcnow()):
    device = Device(device_id=device_id, device_type=device_type, pn_token=pn_token, active=active,
                    user=user, created_at=created_at)
    db.session.add(device)
    db.session.commit()
    return device

def add_group(name):
    group = Group(name=name)
    db.session.add(group)
    db.session.commit()
    return group

def add_user_group_association(user, group):
    user_group_association = UserGroupAssociation(user=user, group=group)
    db.session.add(user_group_association)
    db.session.commit()
    return user_group_association

def set_user_token_hash(user, token):
    user.token_hash = bcrypt.generate_password_hash(token, app.config.get('BCRYPT_LOG_ROUNDS')).decode()
    db.session.commit()
    return user
