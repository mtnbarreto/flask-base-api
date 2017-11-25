# project/api/tasks/push_notification_task.py

from project import db, celery, push_service
from project.models.models import Event
import httplib

@celery.task
def send_async_push_notifications(event):
    pass

def send_push_notifications(event):
    #send_async_push_notifications.delay(event)
    registration_id = event. "<device registration_id>"
    message_title = "Uber update"
    message_body = "Hi john, your customized news for today is ready"
result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
    https://fcm.googleapis.com/v1/projects/myproject-b5ae1/messages:send HTTP/1.1
