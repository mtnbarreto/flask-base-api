# project/tests/test_user_model.py

from sqlalchemy.exc import IntegrityError

from project.extensions import db
from project.models.device import Device
from tests.base import BaseTestCase
from tests.utils import add_device


class TestDeviceModel(BaseTestCase):

    def test_add_device(self):
        device = add_device(device_id="device_id", device_type="apple")
        self.assertTrue(device.id)
        self.assertTrue(device.active)
        self.assertEqual(device.device_id, 'device_id')
        self.assertFalse(device.user)
        self.assertEqual(device.device_type, 'apple')



    def test_add_user_duplicate_device_id(self):
        add_device(device_id="device_id", device_type="apple")
        duplicate_device = Device(device_id="device_id", device_type="android")
        db.session.add(duplicate_device)
        self.assertRaises(IntegrityError, db.session.commit)
