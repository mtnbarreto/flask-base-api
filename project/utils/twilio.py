# project/api/utils/twilio.py

from flask import current_app
from random import randint
from project import twilio_client

def send_sms(to, body):
    message = twilio_client.messages.create(to=to, from_=current_app.config["TWILIO_FROM_NUMBER"], body=body)
    print(message.sid)

def send_account_verification_code(user):
    send_sms(to = user.cell_phone_number, body = "Your verification code is %s" % randint(1000, 9999))
