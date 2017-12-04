# project/api/common/base_definitions.py

import datetime, os, logging
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
