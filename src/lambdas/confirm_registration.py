import json
import time

from ..registration import utils
from structlog import configure, get_logger
from structlog.processors import JSONRenderer

configure(processors=[JSONRenderer()])
logger = get_logger()


def handler(event, context):
    for record in event.get('Records'):
        body = json.loads(record['body'])
        phone_number = body['phonenumber']
        confirmation_code = body['code']
        registration = utils.get_registration(phone_number)

        if confirmation_code != registration['Item']['code']['S']:
            logger.info("confirmation code mismatch", phone_number=phone_number)
            continue
        if time.time() > int(registration['Item']['ttl']['N']):
            logger.info("registration expired", phone_number=phone_number)
            continue

        utils.confirm_registration(phone_number)
        logger.info("confirmed registration", phone_number=phone_number)

    return
