# project/api/v1/email_validation.py

from datetime import datetime
from flask import Blueprint, request, current_app
from flask_accept import accept

from project.extensions import db, bcrypt
from project.api.common.utils.exceptions import InvalidPayload, NotFoundException
from project.api.common.utils.decorators import authenticate
from project.models.user import User
from project.api.common.utils.helpers import session_scope




email_validation_blueprint = Blueprint('email_validation', __name__)

@email_validation_blueprint.route('/email_verification', methods=['PUT'])
@accept('application/json')
@authenticate
def email_verification(user_id):
    ''' creates a email_token_hash and sends email with token to user (assumes login=email), idempotent (could be use for resend)'''
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayload()
    email = post_data.get('email')
    if not email:
        raise InvalidPayload()

    # fetch the user data
    user = User.first_by(email=email)
    if user:
        token = user.encode_email_token()
        with session_scope(db.session):
            user.email_token_hash = bcrypt.generate_password_hash(token, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        if not current_app.testing:
            from project.api.common.utils.mails import send_email_verification_email
            send_email_verification_email(user, token.decode())  # send recovery email
        return {
            'status': 'success',
            'message': 'Successfully sent email with email verification.',
        }
    else:
        raise NotFoundException(message='Login/email does not exist, please write a valid login/email')


@email_validation_blueprint.route('/email_verification/<token>', methods=['GET'])
def verify_email(token):
    ''' creates a email_token_hash and sends email with token to user (assumes login=email), idempotent (could be use for resend)'''
    user_id = User.decode_email_token(token)
    user = User.get(user_id)
    if not user or not user.email_token_hash:
        raise NotFoundException(message='Invalid verification. Please try again.')
    bcrypt.check_password_hash(user.email_token_hash, token)

    with session_scope(db.session):
        user.email_validation_date = datetime.utcnow()
    return {
        'status': 'success',
        'message': 'Successful email verification.',
    }
