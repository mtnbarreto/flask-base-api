# project/api/utils/mails.py

from flask_mail import Message
from flask import render_template, request
from project.tasks.mail_tasks import send_async_registration_email, send_async_password_recovery_email

def send_password_recovery_email(user, token):
    href = request.base_url + '/' + token
    send_async_password_recovery_email.delay(subject="Password Recovery by Flask Base Api! %s" % user.username,
                                    recipient=user.email,
                                     text_body=render_template("auth/password_recovery_user.txt", user=user),
                                     html_body=render_template("auth/password_recovery_user.html", user=user, href=href))





def send_registration_email(user):
    send_async_registration_email.delay(subject="Welcome to Flask Base Api! %s" % user.username,
                     recipient = user.email,
                     text_body = render_template("auth/welcome_new_user.txt", user=user),
                     html_body = render_template("auth/welcome_new_user.html", user=user))
