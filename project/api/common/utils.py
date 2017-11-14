# project/api/common/exceptions.py

from flask import jsonify, request, abort
from functools import wraps
from project.api.common import exceptions
from project.models.models import User

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise exceptions.UnautorizedException() # 'Provide a valid auth token.' 403
        auth_token = auth_header.split(" ")[1]
        resp = User.decode_auth_token(auth_token)
        if isinstance(resp, str):
            raise exceptions.UnautorizedException(message=resp)
        user = User.get(resp)
        if not user or not user.active:
            raise exceptions.UnautorizedException(message='Something went wrong. Please contact us.')
        return f(resp, *args, **kwargs)
    return decorated_function
