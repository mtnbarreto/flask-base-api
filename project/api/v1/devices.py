# project/api/v1/devices.py

from flask import Blueprint, request
from flask_accept import accept

from project.api.common.utils.exceptions import InvalidPayload
from project.models.device import Device
from project.models.user import User
from project.api.common.utils.decorators import authenticate
from project.api.common.utils.helpers import session_scope
from project.extensions import db

devices_blueprint = Blueprint('devices', __name__, template_folder='../templates/devices')


@devices_blueprint.route('/devices', methods=['POST'])
@accept('application/json')
def register_device():
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayload()
    device_id = post_data.get('device_id')
    device_type = post_data.get('device_type')
    if not device_id or not device_type:
        raise InvalidPayload()
    pn_token = post_data.get('pn_token')
    with session_scope(db.session):
        Device.create_or_update(device_id=device_id, device_type=device_type, pn_token=pn_token)
    return {
        'status': 'success',
        'message': 'Device successfully registered.'
    }


@devices_blueprint.route('/devices/<device_id>', methods=['PUT'])
@accept('application/json')
@authenticate
def connect_device_with_logged_in_user(user_id: int, device_id: str):
    user = User.get(user_id)
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayload()
    device_type = post_data.get('device_type')
    if not device_type:
        raise InvalidPayload()
    pn_token = post_data.get('pn_token')
    with session_scope(db.session):
        Device.create_or_update(device_id=device_id, device_type=device_type, user=user, pn_token=pn_token)
    return {
        'status': 'success',
        'message': 'Device successfully registered.'
    }
