# project/api/devices.py

from flask import Flask, Blueprint, jsonify, request
from project.api.common import exceptions
from project.models.models import Device, User
from project.api.common.utils import authenticate

devices_blueprint = Blueprint('devices', __name__, template_folder='../templates/devices')

@devices_blueprint.route('/devices', methods=['POST'])
@authenticate
def register_device(logged_in_user_id):
    post_data = request.get_json()
    if not post_data:
        return exceptions.InvalidPayload()
    device_id   = post_data.get('device_id')
    device_type = post_data.get('device_type')
    pn_token    = post_data.get('pn_token')
    logged_in_user = User.get(logged_in_user_id)
    try:
        device = Device.create_or_update(device_id=device_id, device_type=device_type, pn_token=pn_token, user=logged_in_user, commit=True)
        response_object = {
            'status': 'success',
            'message': 'Device successfully registered.'
        }
        return jsonify(response_object), 200
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        raise exceprions.InvalidPayload()
