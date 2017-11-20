# project/tasks/mail_tasks.py
from flask_mail import Message
from project import celery
from project import mail

@celery.task
def send_async_registration_email(subject, recipients, text_body, html_body):
    msg = Message(subject=subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    return mail.send(msg)
