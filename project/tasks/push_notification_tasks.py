# project/api/tasks/push_notification_tasks.py

from project import celery, push_service


@celery.task
def send_async_push_notifications(message_title, message_body, pn_tokens):
    _ = push_service.notify_multiple_devices(registration_ids=pn_tokens, message_title=message_title, message_body=message_body)
