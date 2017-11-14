# project/tests/utils.py

import datetime

from project import db
from project.models.models import User, Device


def add_user(username, email, password, created_at=datetime.datetime.utcnow()):
    user = User(username=username, email=email, password=password, created_at=created_at)
    db.session.add(user)
    db.session.commit()
    return user

def add_device(device_id, device_type, active=True, pn_token=None, user=None, created_at=datetime.datetime.utcnow()):
    device = Device(device_id=device_id, device_type=device_type, pn_token=pn_token, active=active, user=user, created_at=created_at)
    db.session.add(device)
    db.session.commit()
    return device
