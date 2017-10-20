# project/api/utils/mails.py

from flask_mail import Message
from flask import current_app
from flask import render_template
from project import mail

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def welcome_new_user(user):
    send_email("Welcome to Flask Base Api! %s" % user.username,
               sender = app.config['MAIL_SENDER'],
               recipients = [user.email],
               text_body = render_template("auth/welcome_new_user.txt",
                               user=user),
               html_body = render_template("auth/welcome_new_user.html",
                               user=user))
