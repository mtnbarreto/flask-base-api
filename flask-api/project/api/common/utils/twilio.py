# project/api/common/utils/twilio.py

from project import app
from project.tasks.twilio_tasks import send_async_sms


def send_sms(to, body):
    send_async_sms.delay(to=to, from_=app.config['TWILIO_FROM_NUMBER'], body=body)

def send_cellphone_verification_code(user, validation_code):
    send_sms(to=user.cellphone_cc + user.cellphone_number, body="Your verification code is %s" % validation_code)
