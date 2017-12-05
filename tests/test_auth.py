import json
import time
import uuid

from project import db
from project.models.models import User
from project.utils.constants import Constants
from tests.base import BaseTestCase
from tests.utils import add_user, set_user_token_hash

class TestAuthBlueprint(BaseTestCase):

    def test_user_registration(self):
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict(
                    username='justatest',
                    email='test@test.com',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully registered.')
            self.assertTrue(data['auth_token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_user_registration_duplicate_email(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict(
                    username='michael',
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That user already exists.', data['message'])
            self.assertIn('error', data['status'])

    def test_user_registration_duplicate_username(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict(
                    username='test',
                    email='test@test.com2',
                    password='test'
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That user already exists.', data['message'])
            self.assertIn('error', data['status'])

    def test_user_registration_invalid_json(self):
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict()),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('error', data['status'])

    def test_user_registration_invalid_json_keys_no_username(self):
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict(email='test@test.com',
                                  password='test')),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('error', data['status'])

    def test_user_registration_invalid_json_keys_no_email(self):
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict(
                                    username='justatest',
                                    password='test')),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('error', data['status'])

    def test_user_registration_invalid_json_keys_no_password(self):
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict(
                    username='justatest',
                    email='test@test.com'
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('error', data['status'])


    # Login tests

    def test_registered_user_login(self):
        with self.client:
            user = add_user('test', 'test@test.com', 'test')
            response = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully logged in.')
            self.assertTrue(data['auth_token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_not_registered_user_login(self):
        with self.client:
            response = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'User does not exist.')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 404)



    def test_valid_logout(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            # user login
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            # valid token logout
            response = self.client.get(
                '/v1/auth/logout',
                headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] }
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully logged out.')
            self.assertEqual(response.status_code, 200)


    def test_invalid_logout_expired_token(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            # invalid token logout
            time.sleep(4)
            response = self.client.get(
                '/v1/auth/logout',
                headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] }
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Signature expired. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_invalid_logout(self):
        with self.client:
            response = self.client.get(
                '/v1/auth/logout',
                headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer invalid' })
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid token. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_user_status(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            response = self.client.get(
                '/v1/auth/status',
                headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] }
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['data'] is not None)
            self.assertEqual(data['data']['username'], 'test')
            self.assertEqual(data['data']['email'], 'test@test.com')
            self.assertTrue(data['data']['active'] is True)
            self.assertTrue(data['data']['created_at'])
            self.assertEqual(response.status_code, 200)


    def test_invalid_status(self):
        with self.client:
            response = self.client.get(
                '/v1/auth/status',
                headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer invalid' })
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid token. Please log in again.')
            self.assertEqual(response.status_code, 401)


    def test_add_user_inactive(self):
        add_user('test', 'test@test.com', 'test')
        # update user
        user = User.first_by(email='test@test.com')
        user.active = False
        db.session.commit()
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
                    password='test'
                )),
                content_type='application/json',
                headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] }
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Something went wrong. Please contact us.')
            self.assertEqual(response.status_code, 401)

    def test_password_recovery(self):
        user = add_user('justatest3', 'test@test.com3', 'password')

        with self.client:
            response = self.client.post(
                '/v1/auth/password_recovery',
                data=json.dumps(dict(
                    email='test@test.com3'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully sent email with password recovery.')
            self.assertEqual(response.status_code, 200)

    def test_password_recovery_user_not_registered(self):

        with self.client:
            response = self.client.post(
                '/v1/auth/password_recovery',
                data=json.dumps(dict(
                    email='not_exists@test.com'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn(
                'Login/email does not exist, please write a valid login/email', data['message'])
            self.assertIn('error', data['status'])

    def test_passwords_token_hash_are_random(self):
        add_user('justatest1', 'test@test.com1', 'password')

        with self.client:
            response = self.client.post(
                '/v1/auth/password_recovery',
                data=json.dumps(dict(
                    email='test@test.com1'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully sent email with password recovery.')
            self.assertEqual(response.status_code, 200)

        user = User.query.filter_by(email='test@test.com1').first()
        user_token_hash1 = user.token_hash
        add_user('justatest2', 'test@test.com2', 'password')

        with self.client:
            response = self.client.post(
                '/v1/auth/password_recovery',
                data=json.dumps(dict(
                    email='test@test.com2'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully sent email with password recovery.')
            self.assertEqual(response.status_code, 200)

        user2 = User.query.filter_by(email='test@test.com2').first()

        self.assertTrue(user_token_hash1 != user2.token_hash)
        self.assertTrue(user_token_hash1 is not None)
        self.assertTrue(user_token_hash1 != "")

    def test_password_reset(self):
        user = add_user('justatest3', 'test@test.com3', 'password')
        token = user.encode_password_token(user.id).decode()

        user = set_user_token_hash(user, token)
        user_password = user.password

        with self.client:
            response = self.client.post(
                '/v1/auth/password',
                data=json.dumps(dict(
                    token=token,
                    password='password2'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully reseted password.')
            self.assertEqual(response.status_code, 200)
            #  check db password have really changed
            user_after = User.query.filter_by(id=user.id).first()
            self.assertNotEqual(user_password, user_after.password)

    def test_register_verify_cellphone(self):
        email = 'test@test.com'
        user = add_user('justatest1', email, 'password')

        with self.client:
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email=email,
                    password='password'
                )),
                content_type='application/json'
            )

            response = self.client.post(
                '/v1/auth/cellphone',
                data=json.dumps(dict(
                    cellphone_number='99993298',
                    cellphone_cc='+598'
                )),
                headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] },
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Successfully sent validation code.')
            self.assertEqual(data['status'], 'success')
            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(user.cellphone_validation_code)
            self.assertIsNotNone(user.cellphone_validation_code_expiration)
            self.assertIsNone(user.cellphone_validation_date)

            response = self.client.put(
                '/v1/auth/cellphone/verify',
                data=json.dumps(dict(
                    cellphone_validation_code=user.cellphone_validation_code
                )),
                headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] },
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successful cellphone validation.')
            self.assertIsNone(user.cellphone_validation_code)
            self.assertIsNone(user.cellphone_validation_code_expiration)
            self.assertIsNotNone(user.cellphone_validation_date)


    def test_verify_cellphone_user_already_verified(self):
        email = 'test@test.com'
        user = add_user('justatest1', email, 'password')

        with self.client:
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email=email,
                    password='password'
                )),
                content_type='application/json'
            )

            response = self.client.post(
                '/v1/auth/cellphone',
                data=json.dumps(dict(
                    cellphone_number='99993298',
                    cellphone_cc='+598'
                )),
                content_type='application/json',
                headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] }
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully sent validation code.')
            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(user.cellphone_validation_code)
            self.assertIsNotNone(user.cellphone_validation_code_expiration)
            self.assertIsNone(user.cellphone_validation_date)

        with self.client:
            response = self.client.put(
                '/v1/auth/cellphone/verify',
                data=json.dumps(dict(
                    cellphone_validation_code=user.cellphone_validation_code
                )),
                content_type='application/json',
                headers={ Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] }
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successful cellphone validation.')
            self.assertEqual(response.status_code, 200)
            self.assertIsNone(user.cellphone_validation_code)
            self.assertIsNone(user.cellphone_validation_code_expiration)
            self.assertIsNotNone(user.cellphone_validation_date)

        # try to verify again
        with self.client:
            response = self.client.put(
                '/v1/auth/cellphone/verify',
                data=json.dumps(dict(
                    cellphone_validation_code=user.cellphone_validation_code
                )),
                content_type='application/json',
                headers={Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'] }
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid validation code. Please try again.', data['message'])
            self.assertIn('error', data['status'])
