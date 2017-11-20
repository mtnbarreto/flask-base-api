# project/api/tasks/push_notification_task.py

from project import db, celery
from project.models.models import Event

@celery.task
def send_async_push_notifications(event):
    print('send_async_push_notifications')

def send_push_notifications(event):
    send_async_push_notifications.delay(event)
