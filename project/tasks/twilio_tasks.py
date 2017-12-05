# project/tasks/twilio_tasks.py
from project import celery
from project import twilio_client, app


@celery.task
def send_async_sms(to, from_, body):
    return twilio_client.messages.create(to=to, from_=app.config[‘TWILIO_FROM_NUMBER’], body=body) (edited)
