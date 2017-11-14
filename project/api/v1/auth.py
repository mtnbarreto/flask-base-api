# project/api/auth.py

from flask import Blueprint, jsonify, request, abort, redirect, url_for
from sqlalchemy import exc, or_

from project.models.models import User, Device, UserRole
from project import db, bcrypt
from project.api.common import exceptions
from project.api.common.utils import authenticate, privileges

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/auth/register', methods=['POST'])
def register_user():
    # get post data
    post_data = request.get_json()
    if not post_data:
        raise exceptions.InvalidPayload()
    username = post_data.get('username')
    email = post_data.get('email')
    password = post_data.get('password')
    device_id = post_data.get('device').get('device_id')
    device_type =  post_data.get('device').get('device_type')
    try:
        # check for existing user
        user = User.first(or_(User.username == username, User.email == email))
        if not user:
            # add new user to db
            new_user = User(
                username=username,
                email=email,
                password=password
            )
            db.session.add(new_user)
            Device.create_or_update(device_id=device_id, device_type=device_type, user=user)
            db.session.commit()
            # generate auth token
            auth_token = new_user.encode_auth_token(new_user.id)
            response_object = {
                'status': 'success',
                'message': 'Successfully registered.',
                'auth_token': auth_token.decode()
            }
            return jsonify(response_object), 201
        else:
            # user already registered
            # disable device
            device = Device.first_by(device_id=device_id)
            if device:
                device.active = False
                db.session.commit()

            raise exceptions.BusinessException(message='Sorry. That user already exists.')
    # handler errors
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        raise exceptions.InvalidPayload()


@auth_blueprint.route('/auth/login', methods=['POST'])
def login_user():
    # get post data
    post_data = request.get_json()
    if not post_data:
        raise exceptions.InvalidPayload()
    email = post_data.get('email')
    password = post_data.get('password')
    device_id = post_data.get('device').get('device_id')
    device_type =  post_data.get('device').get('device_type')
    try:
        # fetch the user data
        user = User.first_by(email=email)
        if user and bcrypt.check_password_hash(user.password, password):
            Device.create_or_update(device_id=device_id, device_type=device_type, user=user, commit=True)
            auth_token = user.encode_auth_token(user.id)
            if auth_token:
                response_object = {
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'auth_token': auth_token.decode()
                }
                return jsonify(response_object), 200
        else:
            # user is not logged in, set False to device.active
            device = Device.first_by(device_id=device_id)
            if device:
                device.active = False
                db.session.commit()
            response_object = {
                'status': 'error',
                'message': 'User does not exist.'
            }
            return jsonify(response_object), 404
    except Exception as e:
        print(e)
        response_object = {
            'status': 'error',
            'message': 'Try again.'
        }
        return jsonify(response_object), 500


@auth_blueprint.route('/auth/logout', methods=['GET'])
@authenticate
@privileges(roles = UserRole.USER | UserRole.USER_ADMIN | UserRole.BACKEND_ADMIN)
def logout_user(user_id):
    device_id = request.headers.get('X-Device-Id')
    device = Device.first_by(device_id=device_id)
    if device:
        device.active = False
        db.session.commit()
    response_object = {
        'status': 'success',
        'message': 'Successfully logged out.'
    }
    return jsonify(response_object), 200


@auth_blueprint.route('/auth/status', methods=['GET'])
@authenticate
def get_user_status(user_id):
    user = User.get(user_id)
    response_object = {
        'status': 'success',
        'data': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'active': user.active,
            'created_at': user.created_at
        }
    }
    return jsonify(response_object), 200
