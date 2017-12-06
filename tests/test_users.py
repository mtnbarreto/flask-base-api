# project/tests/test_users.py

import json
import datetime

from project.api.common.utils.constants import Constants
from tests.base import BaseTestCase
from project.models.user import UserRole
from tests.utils import add_user


class TestUsersBlueprint(BaseTestCase):
    """Tests for the Users Service."""

    def test_users(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/v1/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])


    def test_add_user(self):
        """Ensure a new user can be added to the database."""
        add_user('test', 'test@test.com', 'test', roles=UserRole.BACKEND_ADMIN)
        with self.client:
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/v1/users',
                data=json.dumps(dict(
                    username='michael',
                    email='michael@realpython.com',
                    password='password'
                )),
                content_type='application/json',
                headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] }
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('michael@realpython.com was added!', data['message'])
            self.assertIn('success', data['status'])



    def test_add_user_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        add_user('test', 'test@test.com', 'test', roles=UserRole.BACKEND_ADMIN)
        with self.client:
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/v1/users',
                data=json.dumps(dict()),
                content_type='application/json',
                headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] }
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('error', data['status'])

    def test_add_user_invalid_json_keys(self):
        """Ensure error is thrown if the JSON object does not have a username key."""
        add_user('test', 'test@test.com', 'test', roles=UserRole.BACKEND_ADMIN)
        with self.client:
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/v1/users',
                data=json.dumps(dict(email='michael@realpython.com', password='password')),
                content_type='application/json',
                headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] }
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('error', data['status'])

    def test_add_user_duplicate_user(self):
        """Ensure error is thrown if the email already exists."""
        add_user('test', 'test@test.com', 'test', roles=UserRole.BACKEND_ADMIN)
        with self.client:
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            self.client.post(
                '/v1/users',
                data=json.dumps(dict(
                    username='michael',
                    email='michael@realpython.com',
                    password='password'
                )),
                content_type='application/json',
                headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] }
            )
            response = self.client.post(
                '/v1/users',
                data=json.dumps(dict(
                    username='michael',
                    email='michael@realpython.com',
                    password='password'
                )),
                content_type='application/json',
                headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] }
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That email or username already exists.', data['message'])
            self.assertIn('error', data['status'])



    def test_single_user(self):
        """Ensure get single user behaves correctly."""
        user = add_user('michael', 'michael@realpython.com', 'password', roles=UserRole.BACKEND_ADMIN)
        add_user('test', 'test@test.com', 'test', roles=UserRole.BACKEND_ADMIN)
        with self.client:
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            response = self.client.get(f'/v1/users/{user.id}', headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] })
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertIn('michael', data['data']['username'])
            self.assertIn('michael@realpython.com', data['data']['email'])
            self.assertIn('success', data['status'])


    def test_single_user_no_id(self):
        """Ensure error is thrown if an id is not provided."""
        add_user('test', 'test@test.com', 'test', roles=UserRole.BACKEND_ADMIN)
        with self.client:
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            response = self.client.get('/v1/users/blah', headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] })
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist.', data['message'])
            self.assertIn('error', data['status'])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        add_user('test', 'test@test.com', 'test', roles=UserRole.BACKEND_ADMIN)
        with self.client:
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            response = self.client.get('/v1/users/999', headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] })
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist.', data['message'])
            self.assertIn('error', data['status'])


    def test_all_users(self):
        """Ensure get all users behaves correctly."""
        created = datetime.datetime.utcnow() + datetime.timedelta(-30)
        add_user('michael', 'michael@realpython.com', 'password', created_at=created)
        add_user('fletcher', 'fletcher@realpython.com', 'password')
        created = created + datetime.timedelta(-30)
        add_user('test', 'test@test.com', 'test', roles=UserRole.BACKEND_ADMIN, created_at=created)
        with self.client:
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            response = self.client.get('/v1/users', headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] })
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['users']), 3)
            self.assertTrue('created_at' in data['data']['users'][0])
            self.assertTrue('created_at' in data['data']['users'][1])
            self.assertTrue('created_at' in data['data']['users'][2])

            self.assertIn('test', data['data']['users'][2]['username'])
            self.assertIn('test@test.com', data['data']['users'][2]['email'])

            self.assertIn('michael', data['data']['users'][1]['username'])
            self.assertIn('michael@realpython.com', data['data']['users'][1]['email'])

            self.assertIn('fletcher', data['data']['users'][0]['username'])
            self.assertIn('fletcher@realpython.com', data['data']['users'][0]['email'])

            self.assertIn('success', data['status'])
