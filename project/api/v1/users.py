# project/api/v1/users.py

from flask import Blueprint, request
from sqlalchemy import exc, or_
from flask_accept import accept

from project.models.user import User, UserRole
from project import db
from project.api.common.utils.decorators import authenticate, privileges
from project.api.common.utils.exceptions import NotFoundException, BusinessException, InvalidPayload


users_blueprint = Blueprint('users', __name__, template_folder='../templates/users')

@users_blueprint.route('/ping', methods=['GET'])
@accept('application/json')
def ping_pong():
    return {
        'status': 'success',
        'message': 'pong!'
    }

@users_blueprint.route('/push_echo', methods=['POST'])
@accept('application/json')
@authenticate
def push_echo(user_id: int):
    from project.api.common.utils.push_notification import send_notification_to_user
    creator = User.get(user_id)
    send_notification_to_user(user=creator, message_title="Auto Message", message_body="😄😄😄😄😄")
    return {
        'status': 'success',
        'message': 'pong!'
    }
    # from project.api.common.utils.push_notification import send_notifications_for_event
    # from project.models.models import Event
    # from project.api.common.utils.constants import Constants
    # we can also send a notification to a group
    # event = Event(event_descriptor_id=Constants.EventDescriptorIds.SEED_EVENT_ID)
    # creator = User.get(user_id)
    # event.creator = creator
    # event.group = Group.get(1)
    # event.entity_id = creator.id
    # event.entity_description = creator.username
    # event.entity_type = "User"
    # db.session.add(event)
    # db.session.commit()
    # send_notifications_for_event(event=event)

@users_blueprint.route('/users', methods=['POST'])
@accept('application/json')
@authenticate
@privileges(roles=UserRole.BACKEND_ADMIN)
def add_user(_):
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayload()
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
            raise BusinessException(message='Sorry. That email or username already exists.')
    except (exc.IntegrityError, ValueError):
        db.session.rollback()
        raise InvalidPayload()

@users_blueprint.route('/users/<user_id>', methods=['GET'])
@accept('application/json')
@authenticate
@privileges(roles=UserRole.BACKEND_ADMIN)
def get_single_user(_, user_id):
    """Get single user details"""
    try:
        user = User.get(int(user_id))
        if not user:
            raise NotFoundException(message='User does not exist.')
        return {
            'status': 'success',
            'data': {
              'username': user.username,
              'email': user.email,
              'created_at': user.created_at
            }
        }
    except ValueError:
        raise NotFoundException(message='User does not exist.')


@users_blueprint.route('/users', methods=['GET'])
@accept('application/json')
@authenticate
@privileges(roles=UserRole.BACKEND_ADMIN)
def get_all_users(_):
    """Get all users"""
    users = User.query.order_by(User.created_at.desc()).all()
    users_list = [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at
        } for user in users]
    return {
        'status': 'success',
        'data': {
            'users': users_list
        }
    }
