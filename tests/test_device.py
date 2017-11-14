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
