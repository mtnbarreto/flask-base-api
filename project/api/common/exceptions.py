# project/api/common/exceptions.py

class InvalidPayload(Exception):

    def __init__(self, message='Invalid payload.', status_code=400, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv


class BusinessException(Exception):

    def __init__(self, message='Business rule constraint not satified.', status_code=400, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

class UnautorizedException(Exception):

    def __init__(self, message='Not authorized.', payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = 401
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

class InvalidUsage(Exception):
    #status_code = 400

    def __init__(self, message, status_code=400, payload=None):
        Exception.__init__(self)
        self.message = message
        #if status_code is not None:
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
