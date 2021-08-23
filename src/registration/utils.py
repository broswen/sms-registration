import random

import boto3
import os
import time

ddb_client = boto3.client("dynamodb")
sns_client = boto3.client("sns")

expiration_seconds = 60 * 60 * 24


def get_registration(phone_number: str):
    registration = ddb_client.get_item(
        TableName=os.getenv('REGTABLE'),
        Key={
            'phonenumber': {
                'S': phone_number
            }
        }
    )

    return registration


def confirm_registration(phone_number: str):
    ddb_client.update_item(
        TableName=os.getenv('REGTABLE'),
        Key={
            'phonenumber': {
                'S': phone_number
            }
        },
        UpdateExpression="SET #c = :t REMOVE #ttl",
        ExpressionAttributeNames={
            '#c': 'confirmed',
            '#ttl': 'ttl'
        },
        ExpressionAttributeValues={
            ':t': {
                'BOOL': True
            }
        }
    )


def submit_registration(phone_number: str, first_name: str, last_name: str):
    code = random.randint(100000, 1000000)
    ddb_client.put_item(
        TableName=os.getenv('REGTABLE'),
        Item={
            'phonenumber': {
                'S': phone_number
            },
            'firstname': {
                'S': first_name
            },
            'lastname': {
                'S': last_name
            },
            'ttl': {
                'N': str(int(time.time() + expiration_seconds))
            },
            'confirmed': {
                'BOOL': False
            },
            'code': {
                'S': str(code)
            }
        },
        ConditionExpression="attribute_not_exists(phonenumber)"
    )


def send_sms(phone_number: str, message: str):
    sns_client.publish(
        PhoneNumber=phone_number,
        Message=message
    )
