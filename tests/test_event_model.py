# project/tests/test_event_model.py

from project import db
from project.models.event import Event
from project.models.event_descriptor import EventDescriptor
from tests.base import BaseTestCase


class TestEventModel(BaseTestCase):

    def test_add_event(self):
        event_descriptor = EventDescriptor(id=1, name="event_name", description="event_description")
        db.session.add(event_descriptor)
        db.session.commit()

        event = Event(event_descriptor_id=event_descriptor.id)
        db.session.add(event)
        db.session.commit()

        self.assertTrue(event_descriptor.id)
        self.assertTrue(event_descriptor.created_at)
        self.assertTrue(event_descriptor.updated_at)
