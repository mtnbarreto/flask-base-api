# project/api/common/base_definitions.py

import datetime
from flask import Flask, jsonify, Response
from flask.json import JSONEncoder


class BaseJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime.date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

class BaseResponse(Response):
    default_mimetype = 'application/json'

    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, dict):
            rv = jsonify(rv)
        return super(BaseResponse, cls).force_type(rv, environ)


class BaseFlask(Flask):
    response_class = BaseResponse
    json_encoder = BaseJSONEncoder # set up custom encoder to handle date as ISO8601 format
