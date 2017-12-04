# project/__init__.py
import os
import datetime
import logging

from flask import Flask, jsonify, Config, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from twilio.rest import Client
from celery import Celery
from flask_cors import CORS
from raven.contrib.flask import Sentry
from pyfcm import FCMNotification
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

# flask config
conf = Config(root_path=os.path.dirname(os.path.realpath(__file__)))
conf.from_object(os.getenv('APP_SETTINGS'))

# instantiate the extesnions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
mail = Mail()

sentry = None
twilio_client = Client(conf['TWILIO_ACCOUNT_SID'], conf['TWILIO_AUTH_TOKEN'])
push_service = FCMNotification(api_key=conf['FCM_SERVER_KEY'])

def create_app():
    # instantiate the app
    app = BaseFlask(__name__, template_folder='./templates', static_folder='./static')
    # enable CORS
    CORS(app)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # configure sentry
    if not app.debug and not app.testing:
        global sentry
        sentry = Sentry(app, dsn=app.config['SENTRY_DSN'])

    # configure logging
    handler = logging.FileHandler(app.config['LOGGING_LOCATION'])
    handler.setLevel(app.config['LOGGING_LEVEL'])
    handler.setFormatter(logging.Formatter(app.config['LOGGING_FORMAT']))
    app.logger.addHandler(handler)

    # set up extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # register blueprints
    from project.api.v1.auth import auth_blueprint
    from project.api.v1.users import users_blueprint
    from project.api.v1.devices import devices_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/v1')
    app.register_blueprint(users_blueprint, url_prefix='/v1')
    app.register_blueprint(devices_blueprint, url_prefix='/v1')

    # register error handlers
    from project.api.common import exceptions
    from project.api.common import error_handlers
    app.register_error_handler(exceptions.InvalidPayload, error_handlers.handle_exception)
    app.register_error_handler(exceptions.BusinessException, error_handlers.handle_exception)
    app.register_error_handler(exceptions.UnautorizedException, error_handlers.handle_exception)
    app.register_error_handler(exceptions.ForbiddenException, error_handlers.handle_exception)
    app.register_error_handler(exceptions.NotFoundException, error_handlers.handle_exception)
    app.register_error_handler(exceptions.ServerErrorException, error_handlers.handle_exception)
    return app

def make_celery(app):
    app = app or create_app()
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'], include=['project.tasks.mail_tasks', 'project.tasks.push_notification_tasks'])  #backend=conf['CELERY_RESULT_BACKEND']
    # backend=app.config['CELERY_RESULT_BACKEND'] app.import_name
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app = create_app()
celery = make_celery(app)
