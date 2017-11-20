# project/api/auth.py

from flask import Blueprint, jsonify, request, abort, redirect, url_for, current_app
from sqlalchemy import exc, or_

from project import bcrypt, db
from project.api.common import exceptions
from project.api.common.utils import authenticate, privileges
from project.models.models import User, Device, UserRole
from project.utils.mails import password_recovery_user

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
    # current_app.logger.info(post_data.__class__.__name__)
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
            if 'device' in post_data:
                device_id = post_data.get('device').get('device_id')
                device_type =  post_data.get('device').get('device_type')
                Device.create_or_update(device_id=device_id, device_type=device_type, user=user)
                db.session.commit()
            # generate auth token
            auth_token = new_user.encode_auth_token(new_user.id)
            response_object = {
                'status': 'success',
                'message': 'Successfully registered.',
                'auth_token': auth_token.decode()
            }
            # send registration email
            from project.utils.mails import send_registration_email
            send_registration_email(new_user)

            #task = send_async_registration_email.apply_async(countdown=3)

            # mails.send_registration_email(new_user)
            return jsonify(response_object), 201
        else:
            # user already registered
            # disable device
            if 'device' in post_data:
                device_id = post_data.get('device').get('device_id')
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
    if device_id:
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


@auth_blueprint.route('/auth/password', methods=['POST'])
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
            password_recovery_user(user, token.decode())  # send recovery email

            response_object = {
                'status': 'success',
                'message': 'Successfully sent email with password recovery.',
            }

            return jsonify(response_object), 200
        else:
            response_object = {
                'status': 'error',
                'message': 'Login/email does not exist, please write a valid login/email'
            }
            return jsonify(response_object), 404

    except Exception as e:
        raise exceptions.ServerErrorException()


@auth_blueprint.route('/auth/password/', methods=['POST'])
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

            return jsonify(response_object), 200
        else:
            response_object = {
                'status': 'error',
                'message': 'Invalid reset, please try again'
            }
            return jsonify(response_object), 404

    except Exception as e:
        raise exceptions.ServerErrorException()
