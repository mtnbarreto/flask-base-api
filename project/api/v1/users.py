# project/api/views.py

from flask import Flask, Blueprint, jsonify, request, render_template

from project.models.models import User, UserRole, Group
from project import db
from sqlalchemy import exc, or_
from project.api.common.utils import authenticate, privileges

from project.api.common import exceptions


users_blueprint = Blueprint('users', __name__, template_folder='../templates/users')

@users_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

@users_blueprint.route('/push_echo', methods=['POST'])
@authenticate
def push_echo(logged_in_user):
    from project.utils.push_notification import send_notification_to_user
    creator = User.get(logged_in_user)
    send_notification_to_user(user=creator, message_title="Auto Message", message_body="😄😄😄😄😄")(event)
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
    # from project.utils.push_notification import send_notifications_for_event
    # from project.models.models import Event
    # from project.utils.constants import Constants
    # we can also send a notification to a group
    # event = Event(event_descriptor_id=Constants.EventDescriptorIds.SEED_EVENT_ID)
    # creator = User.get(logged_in_user)
    # event.creator = creator
    # event.group = Group.get(1)
    # event.entity_id = creator.id
    # event.entity_description = creator.username
    # event.entity_type = "User"
    # db.session.add(event)
    # db.session.commit()
    # send_notifications_for_event(event=event)

@users_blueprint.route('/users', methods=['POST'])
@authenticate
@privileges(roles=UserRole.BACKEND_ADMIN)
def add_user(logged_in_user):
    post_data = request.get_json()
    if not post_data:
        raise exceptions.InvalidPayload()
    username = post_data.get('username')
    email = post_data.get('email')
    password = post_data.get('password')

    try:
        user = User.first(or_(User.username == username, User.email == email))
        if not user:
            userModel = User(username=username, email=email, password=password)
            db.session.add(userModel)
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': f'{email} was added!'
            }
            return response_object, 201
        else:
            raise exceptions.BusinessException(message='Sorry. That email or username already exists.')
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        raise exceptions.InvalidPayload()

@users_blueprint.route('/users/<user_id>', methods=['GET'])
@authenticate
@privileges(roles=UserRole.BACKEND_ADMIN)
def get_single_user(logged_in_user, user_id):
    """Get single user details"""
    try:
        user = User.get(id=int(user_id))
        if not user:
            raise exceptions.NotFoundException(message='User does not exist.')
        else:
            response_object = {
                'status': 'success',
                'data': {
                  'username': user.username,
                  'email': user.email,
                  'created_at': user.created_at
                }
            }
            return response_object, 200
    except ValueError:
        raise exceptions.NotFoundException(message='User does not exist.')


@users_blueprint.route('/users', methods=['GET'])
@authenticate
@privileges(roles=UserRole.BACKEND_ADMIN)
def get_all_users(*unused):
    """Get all users"""
    users = User.query.order_by(User.created_at.desc()).all()
    users_list = []
    for user in users:
        user_object = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at
        }
        users_list.append(user_object)
    response_object = {
        'status': 'success',
        'data': {
            'users': users_list
        }
    }
    return response_object, 200
