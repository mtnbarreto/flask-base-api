# project/api/common/exceptions.py

class APIException(Exception):

    def __init__(self, message, status_code, payload):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv


class InvalidPayload(APIException):

    def __init__(self, message='Invalid payload.', payload=None):
        super().__init__(message=message, status_code=400, payload=payload)

class BusinessException(APIException):

    def __init__(self, message='Business rule constraint not satified.', payload=None):
        super().__init__(message=message, status_code=400, payload=payload)

class UnautorizedException(APIException):

    def __init__(self, message='Not authorized.', payload=None):
        super().__init__(message=message, status_code=401, payload=payload)

class ForbiddenException(APIException):

    def __init__(self, message='Forbidden.', payload=None):
        super().__init__(message=message, status_code=403, payload=payload)

class NotFoundException(APIException):

    def __init__(self, message='Not Found.', payload=None):
        super().__init__(message=message, status_code=404, payload=payload)
