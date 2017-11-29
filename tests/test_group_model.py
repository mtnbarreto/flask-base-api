# project/tests/test_group_model.py

from sqlalchemy.exc import IntegrityError

from project import db
from project.models.models import User, Group
from tests.base import BaseTestCase
from tests.utils import add_user, add_group, add_user_group_association


class TestGroupModel(BaseTestCase):

    def test_add_group(self):
        group = add_group(name="test_name")
        self.assertTrue(group.id)
        self.assertEqual(group.name, 'test_name')
        self.assertTrue(group.created_at)
        self.assertTrue(group.updated_at)
        self.assertEqual(len(group.associated_users), 0)
        self.assertEqual(len(group.users), 0)

    def test_associated_users(self):
        user = add_user(username="test", email="test@test.com1", password="test")
        group = add_group(name="test_name")
        self.assertEqual(len(group.associated_users), 0)
        user_group_association = add_user_group_association(user=user, group=group)
        self.assertEqual(len(group.associated_users), 1)
        self.assertEqual(group.associated_users[0].user.username, "test")
        self.assertEqual(len(group.users), 1)
        self.assertEqual(group.users[0].username, "test")
        self.assertEqual(len(user.groups), 1)
        self.assertEqual(user.groups[0].name, "test_name")
