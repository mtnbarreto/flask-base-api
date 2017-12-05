# project/api/common/utils/push_notifications.py

import logging
from project.models.models import Event, EventDescriptor, Device
from project.tasks.push_notification_tasks import send_async_push_notifications
from project import db, app

def send_notifications_for_event(event):

    message_title, message_body, pn_tokens = event.push_notification_data()
    event.is_processed = True
    db.session.commit()
    app.logger.info(pn_tokens)
    send_async_push_notifications.delay(message_title=message_title, message_body=message_body, pn_tokens=pn_tokens)


def send_notification_to_user(user, message_title, message_body):
    active_devices = Device.query_active_devices_for_user(user).all()
    pn_tokens = [device.pn_token for device in active_devices]
    send_async_push_notifications.delay(message_title=message_title, message_body=message_body, pn_tokens=pn_tokens)
