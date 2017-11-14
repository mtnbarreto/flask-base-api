# project/models/models.py


import jwt
from datetime import datetime, timedelta
from sqlalchemy import exc, or_
from flask import current_app
from project import db, bcrypt

class Device(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(128), unique=True, nullable=False)
    device_type = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    pn_token = db.Column(db.String(128), unique=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('devices', lazy='joined'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, device_id, device_type, pn_token=None, active=True, user=None, created_at=datetime.utcnow()):
        self.device_id = device_id
        self.device_type = device_type # "apple" "android"
        self.pn_token = pn_token
        self.active = active
        self.user = user
        self.created_at = created_at
        self.updated_at = created_at

    @staticmethod
    def create_or_update(device_id, device_type, user, active=True, commit=False):
        device = Device.query.filter_by(device_id = device_id)
        if not device:
            device = Device(device_id=device_id, device_type=device_type, user=user, active=active)
            db.session.add(device)
        else:
            device.device_type = device_type
            device.user = user
            device.active = active
        if commit:
            db.session.commit()
        device

    @staticmethod
    def first_by(**kwargs):
        """Get first db device that match to device_id"""
        return Device.query.filter_by(**kwargs).first()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(128), nullable=True)
    last_name = db.Column(db.String(128), nullable=True)
    cell_phone_number = db.Column(db.String(128), nullable=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


    def __init__(self, username, email, password, created_at=datetime.utcnow(), cell_phone_number=None):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        self.created_at = created_at
        self.updated_at = created_at
        self.cell_phone_number = cell_phone_number


    def encode_auth_token(self, user_id):
        """Generates the auth token"""
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(
                    days=current_app.config['TOKEN_EXPIRATION_DAYS'], seconds=current_app.config['TOKEN_EXPIRATION_SECONDS']),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """Decodes the auth token - :param auth_token: - :return: integer|string"""
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    @staticmethod
    def first_by(**kwargs):
        """Get first db entity that match to criterium"""
        return User.query.filter_by(**kwargs).first()

    def first(*criterion):
        """Get first db entity that match to criterium"""
        return User.query.filter(*criterion).first()

    @staticmethod
    def get(id):
        """Get db entity that match the id"""
        return User.query.get(id)
