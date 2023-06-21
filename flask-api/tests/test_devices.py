import json
import uuid

from project.models.user import UserRole
from project.models.device import Device
from project.api.common.utils.constants import Constants
from tests.base import BaseTestCase
from tests.utils import add_user


class TestDevicesBlueprint(BaseTestCase):

    def test_device_registration(self):
        with self.client:
            user = add_user(email='test@test.com', password='test', roles=UserRole.USER)
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            device_id = uuid.uuid4().hex
            pn_token = uuid.uuid4().hex
            response = self.client.put(
                f'/v1/devices/{device_id}',
                data=json.dumps(dict(
                    device_id=device_id,
                    device_type='apple',
                    pn_token=pn_token
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.AUTHORIZATION, 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Device successfully registered.')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)

            device = Device.first_by(device_id=device_id)
            self.assertEqual(device.pn_token, pn_token)
            self.assertEqual(device.device_type, 'apple')
            self.assertEqual(device.active, True)
            self.assertEqual(device.user_id, user.id)

    def test_login_with_same_device_id(self):
        """Test that device is removed and added to new device logged user."""
        with self.client:
            user1 = add_user(email='test@test.com', password='test', roles=UserRole.USER)
            user2 = add_user(email='test2@test.com', password='test', roles=UserRole.USER)
            device_id = uuid.uuid4().hex
            self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.DEVICE_ID, device_id), (Constants.HttpHeaders.DEVICE_TYPE, "apple")]
            )
            self.assertEqual(len(user1.devices), 1)

            self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test2@test.com',
                    password='test'
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.DEVICE_ID, device_id), (Constants.HttpHeaders.DEVICE_TYPE, "apple")]
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
            user1 = add_user(email='test@test.com', password='test', roles=UserRole.USER)
            user2 = add_user(email='test2@test.com', password='test', roles=UserRole.USER)
            device_id = uuid.uuid4().hex
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            resp2_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test2@test.com',
                    password='test'
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )

            pn_token = uuid.uuid4().hex
            self.client.put(
                f'/v1/devices/{device_id}',
                data=json.dumps(dict(
                    device_id=device_id,
                    device_type='apple',
                    pn_token=pn_token
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.AUTHORIZATION, 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            response = self.client.put(
                f'/v1/devices/{device_id}',
                data=json.dumps(dict(
                    device_id=device_id,
                    device_type='apple',
                    pn_token=pn_token
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.AUTHORIZATION, 'Bearer ' + json.loads(resp2_login.data.decode())['auth_token'])]
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Device successfully registered.')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)

            self.assertEqual(len(user1.devices), 0)
            self.assertEqual(len(user2.devices), 1)

            self.assertEqual(user2.devices[0].device_id, device_id)
            self.assertEqual(user2.devices[0].device_type, "apple")
            self.assertTrue(user2.devices[0].active)
            self.assertIsNotNone(user2.devices[0].pn_token)
            self.assertEqual(user2.devices[0].user_id, user2.id)

    def test_logout_makes_device_inactive(self):
        user = add_user(email='test@test.com', password='test')
        self.assertEqual(len(user.devices), 0)
        device_id = uuid.uuid4().hex
        with self.client:
            # user login
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.DEVICE_ID, device_id), (Constants.HttpHeaders.DEVICE_TYPE, "apple")]
            )
            self.assertEqual(len(user.devices), 1)
            # valid token logout
            response = self.client.get(
                '/v1/auth/logout',
                headers={
                    'Accept': 'application/json',
                    Constants.HttpHeaders.AUTHORIZATION: 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'],
                    Constants.HttpHeaders.DEVICE_ID: device_id}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Successfully logged out.')
            self.assertEqual(response.status_code, 200)

            self.assertEqual(len(user.devices), 1)

            self.assertEqual(user.devices[0].device_id, device_id)
            self.assertEqual(user.devices[0].device_type, "apple")
            self.assertFalse(user.devices[0].active)
            self.assertIsNone(user.devices[0].pn_token)
            self.assertEqual(user.devices[0].user_id, user.id)
