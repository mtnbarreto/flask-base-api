import json
import time
import uuid

from project import db
from project.models.models import User, UserRole
from tests.base import BaseTestCase
from tests.utils import add_device, add_user

class TestAuthBlueprint(BaseTestCase):

    def test_device_registration(self):
        with self.client:
            add_user('test', 'test@test.com', 'test', roles=UserRole.USER)
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test',
                    device=dict(device_id=uuid.uuid4().hex, device_type="apple")
                )),
                content_type='application/json'
            )
            device_id = uuid.uuid4().hex
            pn_token = uuid.uuid4().hex
            response = self.client.post(
                '/v1/devices',
                data=json.dumps(dict(
                    device_id=device_id,
                    device_type='apple',
                    pn_token=pn_token
                )),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Device successfully registered.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)


    def test_login_with_same_device_id(self):
        """Test that device is removed and added to new device logged user."""
        with self.client:
            user1 = add_user('test', 'test@test.com', 'test', roles=UserRole.USER)
            user2 = add_user('test2', 'test2@test.com', 'test', roles=UserRole.USER)
            device_id = uuid.uuid4().hex
            self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test',
                    device=dict(device_id=device_id, device_type="apple")
                )),
                content_type='application/json'
            )

            self.assertEqual(len(user1.devices), 1)

            self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test2@test.com',
                    password='test',
                    device=dict(device_id=device_id, device_type="apple")
                )),
                content_type='application/json'
            )

            self.assertEqual(len(user1.devices), 0)
            self.assertEqual(len(user2.devices), 1)

            self.assertEqual(user2.devices[0].device_id, device_id)
            self.assertEqual(user2.devices[0].device_type, "apple")
            self.assertTrue(user2.devices[0].active)
            self.assertIsNone(user2.devices[0].pn_token)
            self.assertEqual(user2.devices[0].user_id, user2.id)



    def test_duplicate_device_registration_with_different_users(self):
        with self.client:
            user1  = add_user('test', 'test@test.com', 'test', roles=UserRole.USER)
            user2 = add_user('test2', 'test2@test.com', 'test', roles=UserRole.USER)
            device_id = uuid.uuid4().hex
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test',
                    device=dict(device_id=device_id, device_type="apple")
                )),
                content_type='application/json'
            )
            resp2_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test2@test.com',
                    password='test',
                    device=dict(device_id=device_id, device_type="apple")
                )),
                content_type='application/json'
            )


            pn_token = uuid.uuid4().hex
            self.client.post(
                '/v1/devices',
                data=json.dumps(dict(
                    device_id=device_id,
                    device_type='apple',
                    pn_token=pn_token
                )),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            response = self.client.post(
                '/v1/devices',
                data=json.dumps(dict(
                    device_id=device_id,
                    device_type='apple',
                    pn_token=pn_token
                )),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp2_login.data.decode()
                    )['auth_token']
                )
            )

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Device successfully registered.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

            self.assertEqual(len(user1.devices), 0)
            self.assertEqual(len(user2.devices), 1)

            self.assertEqual(user2.devices[0].device_id, device_id)
            self.assertEqual(user2.devices[0].device_type, "apple")
            self.assertTrue(user2.devices[0].active)
            self.assertIsNotNone(user2.devices[0].pn_token)
            self.assertEqual(user2.devices[0].user_id, user2.id)


    def test_logout_makes_device_inactive(self):
        user = add_user('test', 'test@test.com', 'test')
        self.assertEqual(len(user.devices), 0)
        device_id = uuid.uuid4().hex
        with self.client:
            # user login
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test',
                    device=dict(device_id=device_id, device_type="apple")
                )),
                content_type='application/json'
            )
            self.assertEqual(len(user.devices), 1)
            # valid token logout
            response = self.client.get(
                '/v1/auth/logout',
                headers={
                    "Authorization": 'Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token'],
                    "X-Device-Id": device_id
                }
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged out.')
            self.assertEqual(response.status_code, 200)

            self.assertEqual(len(user.devices), 1)

            self.assertEqual(user.devices[0].device_id, device_id)
            self.assertEqual(user.devices[0].device_type, "apple")
            self.assertFalse(user.devices[0].active)
            self.assertIsNone(user.devices[0].pn_token)
            self.assertEqual(user.devices[0].user_id, user.id)
