# project/api/auth.py

from flask import Blueprint, jsonify, request, abort, redirect, url_for, current_app
from sqlalchemy import exc, or_

from project import bcrypt, db
from project.api.common import exceptions
from project.api.common.utils import authenticate, privileges
from project.models.models import User, Device, UserRole
from project.utils.constants import Constants
from facepy import GraphAPI


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
    if not password:
        raise exceptions.InvalidPayload()
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
            db.session.commit()
            # save the device
            if all(x in request.headers for x in [Constants.HttpHeaders.DEVICE_ID, Constants.HttpHeaders.DEVICE_TYPE]):
                device_id = request.headers.get(Constants.HttpHeaders.DEVICE_ID)
                device_type = request.headers.get(Constants.HttpHeaders.DEVICE_TYPE)
                Device.create_or_update(device_id=device_id, device_type=device_type, user=user)
                db.session.commit()
            # generate auth token
            auth_token = new_user.encode_auth_token()
            # send registration email
            if not current_app.testing:
                from project.utils.mails import send_registration_email
                send_registration_email(new_user)
            response_object = {
                'status': 'success',
                'message': 'Successfully registered.',
                'auth_token': auth_token.decode()
            }
            return response_object, 201
        else:
            # user already registered, set False to device.active
            if Constants.HttpHeaders.DEVICE_ID in request.headers:
                device_id = request.headers.get(Constants.HttpHeaders.DEVICE_ID)
                device = Device.first_by(device_id=device_id)
                if device:
                    device.active = False
                    db.session.commit()
            raise exceptions.BusinessException(message='Sorry. That user already exists.')
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
    if not password:
        raise exceptions.InvalidPayload()
    try:
        # fetch the user data
        user = User.first_by(email=email)
        if user and bcrypt.check_password_hash(user.password, password):
            # register device if needed
            if all(x in request.headers for x in [Constants.HttpHeaders.DEVICE_ID, Constants.HttpHeaders.DEVICE_TYPE]):
                device_id = request.headers.get(Constants.HttpHeaders.DEVICE_ID)
                device_type = request.headers.get(Constants.HttpHeaders.DEVICE_TYPE)
                Device.create_or_update(device_id=device_id, device_type=device_type, user=user)
                db.session.commit()
            auth_token = user.encode_auth_token()
            if auth_token:
                response_object = {
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'auth_token': auth_token.decode()
                }
                return response_object, 200
        else:
            # user is not logged in, set False to device.active
            if Constants.HttpHeaders.DEVICE_ID in request.headers:
                device_id = request.headers.get(Constants.HttpHeaders.DEVICE_ID)
                device = Device.first_by(device_id=device_id)
                if device:
                    device.active = False
                    db.session.commit()
            response_object = {
                'status': 'error',
                'message': 'User does not exist.'
            }
            return response_object, 404
    except Exception as e:
        response_object = {
            'status': 'error',
            'message': 'Try again.'
        }
        return response_object, 500


@auth_blueprint.route('/auth/logout', methods=['GET'])
@authenticate
@privileges(roles = UserRole.USER | UserRole.USER_ADMIN | UserRole.BACKEND_ADMIN)
def logout_user(user_id):
    if Constants.HttpHeaders.DEVICE_ID in request.headers:
        device_id = request.headers.get(Constants.HttpHeaders.DEVICE_ID)
        device = Device.first_by(device_id=device_id)
        if device:
            device.active = False
            db.session.commit()
    response_object = {
        'status': 'success',
        'message': 'Successfully logged out.'
    }
    return response_object, 200


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
    return response_object, 200


@auth_blueprint.route('/auth/password_recovery', methods=['POST'])
def password_recovery():
    ''' creates a password_recovery_hash and sends email to user (assumes login=email)'''
    post_data = request.get_json()
    if not post_data:
        raise exceptions.InvalidPayload()

    email = post_data.get('email')

    try:
        # fetch the user data
        user = User.first_by(email=email)
        if user:
            token = user.encode_password_token(user.id)
            user.token_hash = bcrypt.generate_password_hash(token,
                                                         current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()

            db.session.commit()  # commit token_hash
            if not current_app.testing:
                from project.utils.mails import send_password_recovery_email
                send_password_recovery_email(user, token.decode())  # send recovery email

            response_object = {
                'status': 'success',
                'message': 'Successfully sent email with password recovery.',
            }

            return response_object, 200
        else:
            response_object = {
                'status': 'error',
                'message': 'Login/email does not exist, please write a valid login/email'
            }
            return response_object, 404

    except Exception as e:
        raise exceptions.ServerErrorException()


@auth_blueprint.route('/auth/password', methods=['POST'])
def password_reset():
    ''' reset user password (assumes login=email)'''
    post_data = request.get_json()
    if not post_data:
        raise exceptions.InvalidPayload()

    token = post_data.get('token')
    pw_new = post_data.get('password')

    try:
        # fetch the user data
        user_id = User.decode_password_token(token)
        user = User.query.filter_by(id=user_id).first()
        if user and bcrypt.check_password_hash(user.token_hash, token):
            user.password = bcrypt.generate_password_hash(pw_new,
                                                          current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
            db.session.commit()  # commit new password

            response_object = {
                'status': 'success',
                'message': 'Successfully reseted password.',
            }

            return response_object, 200
        else:
            response_object = {
                'status': 'error',
                'message': 'Invalid reset, please try again'
            }
            return response_object, 404

    except Exception as e:
        raise exceptions.ServerErrorException()


@auth_blueprint.route('/auth/facebook/login', methods=['POST'])
def facebook_login():
    ''' logs in user using fb_access_token returning the corresponding JWT
        if user does not exist registers/creates a new one'''

    post_data = request.get_json()
    if not post_data:
        raise exceptions.InvalidPayload()

    fb_access_token = post_data.get('fb_access_token')

    try:
        graph = GraphAPI(fb_access_token)
        profile = graph.get("me?fields=id,name,email,link")
    except Exception as e:
        raise exceptions.UnautorizedException

    fb_user = User.first(User.fb_id == profile['id'])

    try:
        if not fb_user:
            # Not an existing user so get info, register and login
            user = User.first(User.email == profile['email'])
            code = 200
            if user:
                user.fb_access_token = fb_access_token
                user.fb_id = profile['id']
            else:
                # Create the user and insert it into the database
                user = User(username=profile['name'],
                            email=profile['email'],
                            fb_id=profile['id'],
                            fb_access_token=fb_access_token)
                db.session.add(user)
                code = 201

            db.session.commit()
            # generate auth token
            auth_token = user.encode_auth_token()
            response_object = {
                'status': 'success',
                'message': 'Successfully facebook registered.',
                'auth_token': auth_token.decode()
            }
            return response_object, code
        else:
            auth_token = fb_user.encode_auth_token()
            fb_user.fb_access_token = fb_access_token
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Successfully facebook login.',
                'auth_token': auth_token.decode()
            }
            return response_object, 200
    except Exception as e:
        db.session.rollback()
        raise exceptions.ServerErrorException()
