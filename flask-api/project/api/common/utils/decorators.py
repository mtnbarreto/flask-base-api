# project/api/common/utils/decorators.py

from flask import request
from functools import wraps
from project.api.common.utils.exceptions import UnauthorizedException, ForbiddenException
from project.models.user import User, UserRole


def privileges(roles):
    def actual_decorator(f):
        @wraps(f)
        def decorated_function(logged_user_id, *args, **kwargs):
            user = User.get(logged_user_id)
            if not user or not user.active:
                raise UnauthorizedException(message='Something went wrong. Please contact us.')
            user_roles = UserRole(user.roles)
            if not bool(user_roles & roles):
                raise ForbiddenException()
            return f(logged_user_id, *args, **kwargs)
        return decorated_function
    return actual_decorator

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise UnauthorizedException()
        auth_token = auth_header.split(" ")[1]
        user_id = User.decode_auth_token(auth_token)
        user = User.get(user_id)
        if not user or not user.active:
            raise UnauthorizedException(message='Something went wrong. Please contact us.')
        return f(user_id, *args, **kwargs)
    return decorated_function
