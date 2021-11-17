# project/api/v1/phone_validation.py

from datetime import datetime
from flask import Blueprint, request, current_app
from flask_accept import accept

from project.extensions import db
from project.api.common.utils.exceptions import InvalidPayload, BusinessException
from project.api.common.utils.decorators import authenticate
from project.models.user import User
from project.api.common.utils.helpers import session_scope

phone_validation_blueprint = Blueprint('phone_validation', __name__)

@phone_validation_blueprint.route('/cellphone', methods=['POST'])
@accept('application/json')
@authenticate
def register_user_cellphone(user_id: int):
    ''' generates cellphone_validation_code, idempotent (could be used for resend cellphone_validation_code)
        allows just 1 user per cellphone validation!
    '''
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayload()
    cellphone_number = post_data.get('cellphone_number')
    cellphone_cc = post_data.get('cellphone_cc')
    if not cellphone_number or not cellphone_cc:
        raise InvalidPayload()
    user = User.get(user_id)
    if user.cellphone_validation_date and user.cellphone_number == cellphone_number and user.cellphone_cc == cellphone_cc:
        raise BusinessException(message='Registered. You have already registered this cellphone number.')

    cellphone_validation_code, cellphone_validation_code_expiration = User.generate_cellphone_validation_code()
    with session_scope(db.session) as session:
        user.cellphone_number = cellphone_number
        user.cellphone_cc = cellphone_cc
        user.cellphone_validation_code = cellphone_validation_code
        user.cellphone_validation_code_expiration = cellphone_validation_code_expiration
        user.cellphone_validation_date = None

    if not current_app.testing:
        from project.api.common.utils.twilio import send_cellphone_verification_code
        send_cellphone_verification_code(user, cellphone_validation_code)

    return {
        'status': 'success',
        'message': 'Successfully sent validation code.'
    }


@phone_validation_blueprint.route('/cellphone/verify', methods=['PUT'])
@accept('application/json')
@authenticate
def verify_user_cellphone(user_id: int):
    ''' verifies cellphone_validation_code, idempotent (could be used many times) '''
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayload()
    validation_code = post_data.get('validation_code')
    user = User.get(user_id)

    valid_code, message = user.verify_cellphone_validation_code(validation_code)
    if not valid_code:
        raise BusinessException(message=message)

    with session_scope(db.session) as session:
        user.cellphone_validation_code = None
        user.cellphone_validation_code_expiration = None
        user.cellphone_validation_date = datetime.utcnow()

    return {
        'status': 'success',
        'message': 'Successful cellphone validation.'
    }
