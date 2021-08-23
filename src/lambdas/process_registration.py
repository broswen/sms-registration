import json
from ..registration.utils import send_sms
from structlog import configure, get_logger
from structlog.processors import JSONRenderer

configure(processors=[JSONRenderer()])
logger = get_logger()


def handler(event, context):
    for record in event.get('Records'):
        event_name = record['eventName']
        if event_name not in ['INSERT', 'MODIFY']:
            continue

        phone_number = record['dynamodb']['NewImage']['phonenumber']['S']
        confirmed = record['dynamodb']['NewImage']['confirmed']['BOOL']
        code = record['dynamodb']['NewImage']['code']['S']

        if event_name == 'INSERT':
            message = f'Your confirmation code is {code}.'
            send_sms(phone_number, message)
            logger.info("sent registration code", phone_number=phone_number)
        elif event_name == 'MODIFY' and confirmed:
            message = f'Your registration was successfully confirmed.'
            send_sms(phone_number, message)
            logger.info("sent registration confirmation", phone_number=phone_number)

    return
