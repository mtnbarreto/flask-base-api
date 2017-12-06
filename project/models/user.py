# project/models/user.py

import jwt
from enum import IntFlag
from datetime import datetime, timedelta
from flask import current_app
from project import db, bcrypt
from sqlalchemy.ext.associationproxy import association_proxy
from random import randint
from typing import Tuple, Optional
from project.api.common.utils.exceptions import UnautorizedException, BusinessException

class UserRole(IntFlag):
    USER = 1
    USER_ADMIN = 2
    BACKEND_ADMIN = 4

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    cellphone_number = db.Column(db.String(128))
    cellphone_cc = db.Column(db.String(16))  # cellphone_country_code
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    roles = db.Column(db.Integer, default=UserRole.USER.value, nullable=False)
    password = db.Column(db.String(255), nullable=True)
    token_hash = db.Column(db.String(255), nullable=True)
    fb_id = db.Column(db.String(64), unique=True, nullable=True)  # null if never logged in facebook
    fb_access_token = db.Column(db.String, nullable=True)
    cellphone_validation_code = db.Column(db.String(4))
    cellphone_validation_code_expiration = db.Column(db.DateTime, nullable=True)
    cellphone_validation_date = db.Column(db.DateTime, nullable=True)
    associated_groups = db.relationship("UserGroupAssociation", back_populates="user")
    groups = association_proxy('associated_groups', 'group')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, username: str, email: str, password:str=None, cellphone_number:str=None, cellphone_cc:str=None,
                 fb_id:str=None, fb_access_token:str=None, cellphone_validation_code:str=None,
                 cellphone_validation_code_expiration:datetime=None,
                 cellphone_validation_date:datetime=None, roles:UserRole=UserRole.USER, created_at:datetime=datetime.utcnow()):
        self.username = username
        self.email = email
        if password:
            self.password = bcrypt.generate_password_hash(password,
                                                          current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        self.created_at = created_at
        self.updated_at = created_at
        self.cellphone_number = cellphone_number
        self.cellphone_cc = cellphone_cc
        self.fb_id = fb_id
        self.fb_access_token = fb_access_token
        self.cellphone_validation_code = cellphone_validation_code
        self.cellphone_validation_code_expiration = cellphone_validation_code_expiration
        self.cellphone_validation_date = cellphone_validation_date
        self.roles = roles.value

    @staticmethod
    def first_by(**kwargs):
        """Get first db entity that match to criterium"""
        return User.query.filter_by(**kwargs).first()

    def first(*criterion):
        """Get first db entity that match to criterium"""
        return User.query.filter(*criterion).first()

    @staticmethod
    def get(id: int):
        """Get db entity that match the id"""
        return User.query.get(id)


    def encode_auth_token(self) -> str:
        """Generates the auth token"""
        payload = {
            'exp': datetime.utcnow() + timedelta(
                days=current_app.config['TOKEN_EXPIRATION_DAYS'],
                seconds=current_app.config['TOKEN_EXPIRATION_SECONDS']),
            'iat': datetime.utcnow(),
            'sub': self.id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )


    @staticmethod
    def decode_auth_token(auth_token: str) -> int:
        """Decodes the auth token - :param auth_token: - :return: integer|string"""
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise UnautorizedException(message='Signature expired. Please log in again.')
        except jwt.InvalidTokenError:
            raise UnautorizedException(message='Invalid token. Please log in again.')

    def encode_password_token(self) -> str:
        """Generates the auth token"""
        payload = {
            'exp': datetime.utcnow() + timedelta(
                days=current_app.config['TOKEN_PASSWORD_EXPIRATION_DAYS'],
                seconds=current_app.config['TOKEN_PASSWORD_EXPIRATION_SECONDS']),
            'iat': datetime.utcnow(),
            'sub': self.id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

    @staticmethod
    def decode_password_token(pass_token: str) -> int:
        """Decodes the auth token - :param auth_token: - :return: integer|string"""
        try:
            payload = jwt.decode(pass_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise BusinessException(message='Password recovery token expired. Please try again.')
        except jwt.InvalidTokenError:
            raise BusinessException(message='Invalid password recovery token. Please try again.')

    @staticmethod
    def generate_cellphone_validation_code() -> Tuple[str, datetime]:
        """Generates cell phone number validation code and expiration time"""
        return str(randint(1000, 9999)), datetime.utcnow() + timedelta(seconds=current_app.config['CELLPHONE_VALIDATION_CODE_EXP_SECS'])

    def verify_cellphone_validation_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """Validates that code matches with user.cellphone_validation_code and its not expired"""
        if not self.cellphone_validation_code or self.cellphone_validation_code != code:
            return False, 'Invalid validation code. Please try again.'

        delta = datetime.utcnow() + timedelta(seconds=current_app.config['CELLPHONE_VALIDATION_CODE_EXP_SECS'])
        if not self.cellphone_validation_code_expiration or self.cellphone_validation_code_expiration > delta:
            return False, 'Validation expired. Please try again.'

        return True, None