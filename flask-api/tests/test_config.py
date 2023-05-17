# project/tests/test_config.py

import unittest
import os
from project import app
from flask_testing import TestCase


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertIsNotNone(app)
        self.assertEqual(app.config['SECRET_KEY'], os.environ.get('SECRET_KEY'))
        self.assertTrue(app.config['DEBUG'])
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], os.environ.get('DATABASE_URL'))
        self.assertEqual(app.config['BCRYPT_LOG_ROUNDS'], 4)
        self.assertEqual(app.config['TOKEN_EXPIRATION_DAYS'], 30)
        self.assertEqual(app.config['TOKEN_EXPIRATION_SECONDS'], 0)


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertEqual(app.config['SECRET_KEY'], os.environ.get('SECRET_KEY'))
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['TESTING'])
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], os.environ.get('DATABASE_TEST_URL'))
        self.assertEqual(app.config['BCRYPT_LOG_ROUNDS'], 4)
        self.assertEqual(app.config['TOKEN_EXPIRATION_DAYS'], 0)
        self.assertEqual(app.config['TOKEN_EXPIRATION_SECONDS'], 3)


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertTrue(app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY'))
        self.assertFalse(app.config['DEBUG'])
        self.assertFalse(app.config['TESTING'])
        self.assertEqual(app.config['BCRYPT_LOG_ROUNDS'], 13)
        self.assertEqual(app.config['TOKEN_EXPIRATION_DAYS'], 30)
        self.assertEqual(app.config['TOKEN_EXPIRATION_SECONDS'], 0)


