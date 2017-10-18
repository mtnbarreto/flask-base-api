# project/__init__.py
import os
import datetime

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from celery import Celery

# instantiate the extesnions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app():
    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    #import pdb; pdb.set_trace()

    # set up extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from project.api.auth import auth_blueprint
    from project.api.users import users_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(users_blueprint)

    return app


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
    # celery.app = app
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
