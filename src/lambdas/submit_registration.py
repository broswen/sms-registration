import json
from ..registration import utils
from botocore.exceptions import ClientError
from structlog import configure, get_logger
from structlog.processors import JSONRenderer

configure(processors=[JSONRenderer()])
logger = get_logger()


def handler(event, context):
    for record in event.get('Records'):
        body = json.loads(record.get('body'))
        try:
            utils.submit_registration(body['phonenumber'], body['firstname'], body['lastname'])
        except ClientError as err:
            print(err)
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                logger.warning("already registered", phone_number=body['phonenumber'])
                continue
            raise err
        else:
            logger.info("submitted registration", phone_number=body['phonenumber'])
    # put item with details into registration table
    # error if already exists, and not expired
    # overwrite if exists but expired

    return
