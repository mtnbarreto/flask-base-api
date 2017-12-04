# project/api/devices.py

from flask import Flask, Blueprint, jsonify, request
from project.api.common import exceptions
from project.models.models import Device, User
from project.api.common.utils import authenticate
from project import db

devices_blueprint = Blueprint('devices', __name__, template_folder='../templates/devices')


@devices_blueprint.route('/devices', methods=['POST'])
def register_device():
    post_data = request.get_json()
    if not post_data:
        return exceptions.InvalidPayload()
    device_id   = post_data.get('device_id')
    device_type = post_data.get('device_type')
    if not device_id or not device_type:
        return exceptions.InvalidPayload()
    pn_token    = post_data.get('pn_token')
    try:
        device = Device.create_or_update(device_id=device_id, device_type=device_type, pn_token=pn_token)
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': 'Device successfully registered.'
        }
        return jsonify(response_object), 200
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        raise exceprions.InvalidPayload()

@devices_blueprint.route('/devices/<device_id>', methods=['PUT'])
@authenticate
def connect_device_with_logged_in_user(logged_in_user_id, device_id):
    logged_in_user = User.get(logged_in_user_id)
    post_data = request.get_json()
    if not post_data:
        return exceptions.InvalidPayload()
    device_type = post_data.get('device_type')
    if not device_type:
        return exceptions.InvalidPayload()
    pn_token = post_data.get('pn_token')
    try:
        device = Device.create_or_update(device_id=device_id, device_type=device_type, user=logged_in_user, pn_token=pn_token)
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': 'Device successfully registered.'
        }
        return jsonify(response_object), 200
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        raise exceprions.InvalidPayload()
