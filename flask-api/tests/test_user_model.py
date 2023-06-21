# project/tests/test_user_model.py

from sqlalchemy.exc import IntegrityError

from project.extensions import db
from project.models.user import User
from tests.base import BaseTestCase
from tests.utils import add_user


class TestUserModel(BaseTestCase):

    def test_add_user(self):
        user = add_user(email='test@test.com', password='password')
        self.assertTrue(user.id)
        self.assertEqual(user.email, 'test@test.com')
        self.assertTrue(user.password)
        self.assertTrue(user.active)
        self.assertTrue(user.created_at)

    def test_add_user_duplicate_email(self):
        add_user(email='test@test.com', password='password')
        duplicate_user = User(
            email='test@test.com',
            password='password'
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)


    def test_passwords_are_random(self):
        user_one = add_user(email='test@test.com', password='password')
        user_two = add_user(email='test@test2.com', password='password')
        self.assertNotEqual(user_one.password, user_two.password)

    def test_encode_auth_token(self):
        user = add_user(email='test@test.com', password='test')
        auth_token = user.encode_auth_token()
        self.assertTrue(isinstance(auth_token, str))


    def test_decode_auth_token(self):
        user = add_user(email='test@test.com', password='test')
        auth_token = user.encode_auth_token()
        self.assertTrue(isinstance(auth_token, str))
        self.assertTrue(User.decode_auth_token(auth_token), user.id)
