# project/api/common/utils/push_notifications.py

from project import app
from project.extensions import db
from project.models.event import Event
from project.models.user import User
from project.models.device import Device
from project.tasks.push_notification_tasks import send_async_push_notifications


def send_notifications_for_event(event: Event):
    message_title, message_body, pn_tokens = event.push_notification_data()
    event.is_processed = True
    db.session.commit()
    app.logger.info(pn_tokens)
    send_async_push_notifications.delay(message_title=message_title, message_body=message_body, pn_tokens=pn_tokens)


def send_notification_to_user(user: User, message_title: str, message_body: str):
    active_devices = Device.query_active_devices_for_user(user).all()
    pn_tokens = [device.pn_token for device in active_devices]
    send_async_push_notifications.delay(message_title=message_title, message_body=message_body, pn_tokens=pn_tokens)
