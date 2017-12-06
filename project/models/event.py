# project/models/event.py


from datetime import datetime
from project import db
from project.models.device import Device

class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    event_descriptor_id = db.Column(db.Integer, db.ForeignKey('event_descriptors.id'), nullable=False)
    event_descriptor = db.relationship('EventDescriptor', backref=db.backref('events', lazy='joined'))

    entity_type = db.Column(db.String(128))
    entity_id = db.Column(db.Integer)
    entity_description = db.Column(db.String(128))
    entity_2_type = db.Column(db.String(128))
    entity_2_id = db.Column(db.Integer)
    entity_2_description = db.Column(db.String(128))
    entity_3_type = db.Column(db.String(128))
    entity_3_id = db.Column(db.Integer)
    entity_3_description = db.Column(db.String(128))
    expiration_date = db.Column(db.DateTime)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    group = db.relationship('Group', backref=db.backref('events', lazy='joined'))
    is_processed = db.Column(db.Boolean, default=False, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    creator = db.relationship('User', backref=db.backref('events', lazy='joined'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, event_descriptor_id: int):
        self.event_descriptor_id = event_descriptor_id

    def push_notification_data(self):
        event_descriptor = self.event_descriptor
        message_template = event_descriptor.description
        if self.entity_description:
            message_template = message_template.replace("{1}", self.entity_description)
        if self.entity_2_description:
            message_template = message_template.replace("{2}", self.entity_2_description)
        if self.entity_3_description:
            message_template = message_template.replace("{3}", self.entity_3_description)
        devices = Device.query_active_devices_for_group(group=self.group, discard_user_ids=[self.creator_id]).all()
        pn_tokens = [device.pn_token for device in devices]
        return "Hi", message_template, pn_tokens