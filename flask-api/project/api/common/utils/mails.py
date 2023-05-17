# project/api/common/utils/mails.py

from flask import render_template, request, url_for
from project.tasks.mail_tasks import send_async_registration_email, send_async_password_recovery_email, send_async_email_verification_email


def send_password_recovery_email(user, token):
    href = request.base_url + '/' + token
    send_async_password_recovery_email.delay(subject="Password Recovery by Flask Base Api! %s" % user.username,
                                             recipient=user.email,
                                             text_body=render_template("auth/password_recovery_user.txt", user=user),
                                             html_body=render_template("auth/password_recovery_user.html", user=user, href=href))

def send_registration_email(user, token):
    href = request.url_root + url_for('email_validation.verify_email', token='')[1:] + token
    send_async_registration_email.delay(subject="Welcome by Flask Base Api! %s" % user.username,
                                        recipient=user.email,
                                        text_body=render_template("auth/welcome_new_user.txt", user=user),
                                        html_body=render_template("auth/welcome_new_user.html", user=user, href=href))

def send_email_verification_email(user, token):
    href = request.base_url + '/' + token
    send_async_email_verification_email.delay(subject="Email confirmation by Flask Base Api! %s" % user.username,
                                              recipient=user.email,
                                              text_body=render_template("auth/email_verification_user.txt", user=user),
                                              html_body=render_template("auth/email_verification_user.html", user=user, href=href))
