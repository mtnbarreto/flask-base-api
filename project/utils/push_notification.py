from apns2.client import APNsClient
from apns2.payload import Payload
from apns2.errors import ConnectionFailed, BadDeviceToken, PayloadTooLarge, DeviceTokenNotForTopic
import logging


class PushNotification(object):

    client = APNsClient('key.pem', use_sandbox=False, use_alternative_port=False)

    def __init__(self, device, payload):
        self.device = device
        self.payload = payload



# token_hex = 'b5bb9d8014a0f9b1d61e21e796d78dccdf1352f23cd32812f4850b87'
# payload = Payload(alert="Hello World!", sound="default", badge=1)
# topic = 'com.example.App'
# client =
# client.send_notification(token_hex, payload, topic)
