# project/api/common/utils/decorators.py

from flask import jsonify, request, abort
from functools import wraps
from project.api.common.utils import exceptions
from project.models.models import User, UserRole


def privileges(roles):
    def actual_decorator(f):
        @wraps(f)
        def decorated_function(logged_user_id, *args, **kwargs):
            user = User.get(logged_user_id)
            if not user or not user.active:
                raise exceptions.UnautorizedException(message='Something went wrong. Please contact us.')
            user_roles = UserRole(user.roles)
            if not bool(user_roles & roles):
                raise exceptions.ForbiddenException()
            return f(logged_user_id, *args, **kwargs)
        return decorated_function
    return actual_decorator

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
