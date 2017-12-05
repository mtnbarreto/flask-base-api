# project/__init__.py
import os

from flask import Flask, Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from twilio.rest import Client
from celery import Celery
from raven.contrib.flask import Sentry
from pyfcm import FCMNotification
from project.api.common.base_definitions import BaseFlask

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
    app = BaseFlask(__name__)

    # configure sentry
    if not app.debug and not app.testing:
        global sentry
        sentry = Sentry(app, dsn=app.config['SENTRY_DSN'])

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
    from project.api.common.utils import exceptions
    from project.api.common import error_handlers
    app.register_error_handler(exceptions.InvalidPayload, error_handlers.handle_exception)
    app.register_error_handler(exceptions.BusinessException, error_handlers.handle_exception)
    app.register_error_handler(exceptions.UnautorizedException, error_handlers.handle_exception)
    app.register_error_handler(exceptions.ForbiddenException, error_handlers.handle_exception)
    app.register_error_handler(exceptions.NotFoundException, error_handlers.handle_exception)
    app.register_error_handler(exceptions.ServerErrorException, error_handlers.handle_exception)
    #app.register_error_handler(Exception, error_handlers.handle_general_exception)
    return app

def make_celery(app):
    app = app or create_app()
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'], include=['project.tasks.mail_tasks', 'project.tasks.push_notification_tasks',
                    'project.tasks.twilio_tasks'], backend=app.config['CELERY_RESULT_BACKEND'])
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
