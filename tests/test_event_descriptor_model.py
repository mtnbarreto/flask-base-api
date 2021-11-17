# project/tests/test_event_descriptor_model.py

from sqlalchemy.exc import IntegrityError
from project.extensions import db
from project.models.event import Event
from project.models.event_descriptor import EventDescriptor
from tests.base import BaseTestCase


class TestEventDescriptorModel(BaseTestCase):

    def test_add_event_descriptor(self):
        event_descriptor = EventDescriptor(id = 1, name="event_name", description="event_description")
        db.session.add(event_descriptor)
        db.session.commit()

        self.assertTrue(event_descriptor.id)
        self.assertEqual(event_descriptor.name, 'event_name')
        self.assertEqual(event_descriptor.description, 'event_description')

    def test_event_descriptor_relations(self):
        event_descriptor = EventDescriptor(id = 1, name="event_name", description="event_description")
        db.session.add(event_descriptor)
        db.session.commit()

        event = Event(event_descriptor_id=33)
        db.session.add(event)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

        event.event_descriptor_id = event_descriptor.id
        db.session.add(event)
        db.session.commit()

        self.assertTrue(event.id)
        self.assertTrue(event.created_at)
        self.assertTrue(event.updated_at)

        self.assertEqual(event.event_descriptor.id, event_descriptor.id)

        event = Event(event_descriptor_id=event_descriptor.id)
        db.session.add(event)
        db.session.commit()

        self.assertTrue(event.id)
        self.assertTrue(event.created_at)
        self.assertTrue(event.updated_at)

        self.assertEqual(len(event_descriptor.events), 2)
