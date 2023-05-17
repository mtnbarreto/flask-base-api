# project/api/common/base_definitions.py

import datetime, os, logging
from flask import Flask, jsonify, Response
from flask_cors import CORS
from flask.json.provider import JSONProvider
import orjson

class OrJSONProvider(JSONProvider):
    def dumps(self, obj, *, option=None, **kwargs):
        if option is None:
            option = orjson.OPT_APPEND_NEWLINE | orjson.OPT_NAIVE_UTC
        
        return orjson.dumps(obj, option=option).decode()

    def loads(self, s, **kwargs):
        return orjson.loads(s)

class BaseResponse(Response):
    default_mimetype = 'application/json'

    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, dict):
            rv = jsonify(rv)
        return super(BaseResponse, cls).force_type(rv, environ)


class BaseFlask(Flask):
    response_class = BaseResponse
    json_provider_class = OrJSONProvider

    def __init__(
        self,
        import_name
    ):
        Flask.__init__(
            self,
            import_name,
            static_folder='./static',
            template_folder='./templates'
        )
        # set config
        app_settings = os.getenv('APP_SETTINGS')
        self.config.from_object(app_settings)

        # configure logging
        handler = logging.FileHandler(self.config['LOGGING_LOCATION'])
        handler.setLevel(self.config['LOGGING_LEVEL'])
        handler.setFormatter(logging.Formatter(self.config['LOGGING_FORMAT']))
        self.logger.addHandler(handler)

        # enable CORS
        CORS(self)
