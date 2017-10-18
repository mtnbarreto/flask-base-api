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
# app = create_app()
# celery = set_up_celery()


def create_app():
    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

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

# def set_up_celery():
#     celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
#     celery.conf.update(app.config)
#     return celery
