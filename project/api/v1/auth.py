# project/api/auth.py

from flask import Blueprint, jsonify, request, abort, redirect, url_for, current_app
from sqlalchemy import exc, or_

from project import bcrypt, db
from project.api.common import exceptions
from project.api.common.utils import authenticate, privileges
from project.models.models import User, Device, UserRole
from project.utils.constants import Constants
from facepy import GraphAPI
from datetime import datetime
from project.utils.helpers import session_scope

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
    if not password or not username or not email:
        raise exceptions.InvalidPayload()
    # check for existing user
    user = User.first(or_(User.username == username, User.email == email))
    if not user:
        # add new user to db
        new_user = User(username=username, email=email, password=password)
        with session_scope(db.session) as session:
            session.add(new_user)
        # save the device
        if all(x in request.headers for x in [Constants.HttpHeaders.DEVICE_ID, Constants.HttpHeaders.DEVICE_TYPE]):
            device_id = request.headers.get(Constants.HttpHeaders.DEVICE_ID)
            device_type = request.headers.get(Constants.HttpHeaders.DEVICE_TYPE)
            with session_scope(db.session) as session:
                Device.create_or_update(device_id=device_id, device_type=device_type, user=user)
        # generate auth token
        auth_token = new_user.encode_auth_token()
        # send registration email
        if not current_app.testing:
            from project.utils.mails import send_registration_email
            send_registration_email(new_user)
        return {
            'status': 'success',
            'message': 'Successfully registered.',
            'auth_token': auth_token.decode()
        }, 201
    else:
        # user already registered, set False to device.active
        if Constants.HttpHeaders.DEVICE_ID in request.headers:
            device_id = request.headers.get(Constants.HttpHeaders.DEVICE_ID)
            device = Device.first_by(device_id=device_id)
            if device:
                with session_scope(db.session) as session:
                    device.active = False
        raise exceptions.BusinessException(message='Sorry. That user already exists.')


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

    # fetch the user data
    user = User.first_by(email=email)
    if user and bcrypt.check_password_hash(user.password, password):
        # register device if needed
        if all(x in request.headers for x in [Constants.HttpHeaders.DEVICE_ID, Constants.HttpHeaders.DEVICE_TYPE]):
            device_id = request.headers.get(Constants.HttpHeaders.DEVICE_ID)
            device_type = request.headers.get(Constants.HttpHeaders.DEVICE_TYPE)
            with session_scope(db.session) as session:
                Device.create_or_update(device_id=device_id, device_type=device_type, user=user)
        auth_token = user.encode_auth_token()
        if auth_token:
            return {
                'status': 'success',
                'message': 'Successfully logged in.',
                'auth_token': auth_token.decode()
            }, 200
    else:
        # user is not logged in, set False to device.active
        if Constants.HttpHeaders.DEVICE_ID in request.headers:
            device_id = request.headers.get(Constants.HttpHeaders.DEVICE_ID)
            device = Device.first_by(device_id=device_id)
            if device:
                with session_scope(db.session) as session:
                    device.active = False
        raise exceptions.NotFoundException(message='User does not exist.')


@auth_blueprint.route('/auth/logout', methods=['GET'])
@authenticate
@privileges(roles = UserRole.USER | UserRole.USER_ADMIN | UserRole.BACKEND_ADMIN)
def logout_user(user_id):
    if Constants.HttpHeaders.DEVICE_ID in request.headers:
        device_id = request.headers.get(Constants.HttpHeaders.DEVICE_ID)
        device = Device.first_by(device_id=device_id)
        if device:
            with session_scope(db.session) as session:
                device.active = False
    return {
        'status': 'success',
        'message': 'Successfully logged out.'
    }, 200


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
    if not email:
        raise exceptions.InvalidPayload()

    # fetch the user data
    user = User.first_by(email=email)
    if user:
        token = user.encode_password_token(user.id)
        with session_scope(db.session) as session:
            user.token_hash = bcrypt.generate_password_hash(token,
                                                         current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        if not current_app.testing:
            from project.utils.mails import send_password_recovery_email
            send_password_recovery_email(user, token.decode())  # send recovery email
        return {
            'status': 'success',
            'message': 'Successfully sent email with password recovery.',
        }, 200
    else:
        raise exceptions.NotFoundException(message='Login/email does not exist, please write a valid login/email')


@auth_blueprint.route('/auth/password', methods=['POST'])
def password_reset():
    ''' reset user password (assumes login=email)'''
    post_data = request.get_json()
    if not post_data:
        raise exceptions.InvalidPayload()
    token = post_data.get('token')
    pw_new = post_data.get('password')
    if not token or not pw_new:
        raise exceptions.InvalidPayload()

    # fetch the user data
    user_id = User.decode_password_token(token)
    user = User.get(user_id)
    if user and bcrypt.check_password_hash(user.token_hash, token):
        with session_scope(db.session) as session:
            user.password = bcrypt.generate_password_hash(pw_new, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        return {
            'status': 'success',
            'message': 'Successfully reseted password.',
        }, 200
    else:
        raise exceptions.NotFoundException(message='Invalid reset, please try again')



@auth_blueprint.route('/auth/facebook/login', methods=['POST'])
def facebook_login():
    ''' logs in user using fb_access_token returning the corresponding JWT
        if user does not exist registers/creates a new one'''

    post_data = request.get_json()
    if not post_data:
        raise exceptions.InvalidPayload()
    fb_access_token = post_data.get('fb_access_token')
    if not fb_access_token:
        raise exceptions.InvalidPayload()
    try:
        graph = GraphAPI(fb_access_token)
        profile = graph.get("me?fields=id,name,email,link")
    except Exception as e:
        raise exceptions.UnautorizedException

    fb_user = User.first(User.fb_id == profile['id'])
    if not fb_user:
        # Not an existing user so get info, register and login
        user = User.first(User.email == profile['email'])
        code = 200
        with session_scope(db.session) as session:
            if user:
                user.fb_access_token = fb_access_token
                user.fb_id = profile['id']
            else:
                # Create the user and insert it into the database
                user = User(username=profile['name'],
                            email=profile['email'],
                            fb_id=profile['id'],
                            fb_access_token=fb_access_token)
                session.add(user)
                code = 201
        # generate auth token
        auth_token = user.encode_auth_token()
        return {
            'status': 'success',
            'message': 'Successfully facebook registered.',
            'auth_token': auth_token.decode()
        }, code
    else:
        auth_token = fb_user.encode_auth_token()
        with session_scope(db.session) as session:
            fb_user.fb_access_token = fb_access_token
        return {
            'status': 'success',
            'message': 'Successfully facebook login.',
            'auth_token': auth_token.decode()
        }, 200


@auth_blueprint.route('/auth/cellphone', methods=['POST'])
@authenticate
def register_user_cellphone(user_id):
    ''' generates cellphone_validation_code, idempotent (could be used for resend cellphone_validation_code)
        allows just 1 user per cellphone validation!
    '''
    post_data = request.get_json()
    if not post_data:
        raise exceptions.InvalidPayload()
    cellphone_number = post_data.get('cellphone_number')
    cellphone_cc = post_data.get('cellphone_cc')
    if not cellphone_number or not cellphone_cc:
        raise exceptions.InvalidPayload()
    user = User.get(user_id)
    if user.cellphone_validation_date and user.cellphone_number == cellphone_number and user.cellphone_cc == cellphone_cc:
        raise exceptions.BusinessException(message='Registered. You have already registered this cellphone number.')

    cellphone_validation_code, cellphone_validation_code_expiration = User.generate_cellphone_validation_code()
    with session_scope(db.session) as session:
        user.cellphone_number = cellphone_number
        user.cellphone_cc = cellphone_cc
        user.cellphone_validation_code = cellphone_validation_code
        user.cellphone_validation_code_expiration = cellphone_validation_code_expiration
        user.cellphone_validation_date = None

    if current_app.testing:
        from project.utils.twilio import send_cellphone_verification_code
        send_cellphone_verification_code(user, cellphone_validation_code)

    return {
        'status': 'success',
        'message': 'Successfully sent validation code.'
    }, 200


@auth_blueprint.route('/auth/cellphone/verify', methods=['PUT'])
@authenticate
def verify_user_cellphone(user_id):
    ''' verifies cellphone_validation_code, idempotent (could be used many times) '''
    post_data = request.get_json()
    if not post_data:
        raise exceptions.InvalidPayload()

    validation_code = post_data.get('cellphone_validation_code')
    user = User.get(user_id)

    valid_code, message = user.verify_cellphone_validation_code(validation_code)
    if not valid_code:
        raise exceptions.BusinessException(message=message)

    with session_scope(db.session) as session:
        user.cellphone_validation_code = None
        user.cellphone_validation_code_expiration = None
        user.cellphone_validation_date = datetime.utcnow()

    return {
        'status': 'success',
        'message': 'Successful cellphone validation.'
    }, 200
