
import json
from tests.base import BaseTestCase

class TestHttpResponse(BaseTestCase):

    def test_wrong_accept_type(self):
        with self.client:
            response = self.client.get('/v1/ping', headers=[('Accept', 'application/json')])
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'pong!')
            self.assertEqual(response.content_type, 'application/json')


            response = self.client.get('/v1/ping', headers=[('Accept', 'application/json, */*')])
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'pong!')
            self.assertEqual(response.content_type, 'application/json')


            response = self.client.get('/v1/ping', headers=[('Accept', '*/*')])
            self.assertEqual(response.status_code, 406)
            self.assertEqual(response.content_type, 'text/html')

            response = self.client.get('/v1/ping', headers=[('Accept', 'text/html')])
            self.assertEqual(response.status_code, 406)
            self.assertEqual(response.content_type, 'text/html')
