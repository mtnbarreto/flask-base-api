# project/tests/base.py

import os
os.environ["APP_SETTINGS"] = "project.config.TestingConfig"
from flask_testing import TestCase
from project import app
from project.extensions import db

class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
