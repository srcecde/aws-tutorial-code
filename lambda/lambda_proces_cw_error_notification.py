"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""

import os
import gzip
import base64
import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def process_event(event: dict) -> dict:
    # Parse event by decoding, decompressing
    decoded_payload = base64.b64decode(event.get("awslogs").get("data"))
    uncompressed_payload = gzip.decompress(decoded_payload)
    payload = json.loads(uncompressed_payload)
    return payload


def process_error_payload(
    payload: dict,
) -> str("Returns parsed response from payload!"):
    # Parse payload to extract necessary information
    logGroup = payload.get("logGroup")
    logStream = payload.get("logStream")
    logEvents = payload.get("logEvents")
    lambda_function_name = payload.get("logGroup").split("/")[-1]
    error_msg = "\t".join(levent["message"] for levent in logEvents)
    return logGroup, logStream, lambda_function_name, error_msg


def return_func(
    status_code=200,
    message="Awesome, you did it! Thanks from Srce Cde!",
    headers={"Content-Type": "application/json"},
    isBase64Encoded=False,
) -> dict:
    # Helper function for return statement
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps({"message": message}),
        "isBase64Encoded": isBase64Encoded,
    }


def send_email(
    logGroup: str,
    logStream: str,
    lambda_function_name: str,
    error_msg: str,
) -> str("Send an email notification, if successful!"):
    # Sends email notification
    sns_client = boto3.client("sns")
    SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", None)
    if not SNS_TOPIC_ARN:
        logger.error("SNS_TOPIC_ARN is missing!")
        return return_func(status_code=500, message="Error sending notification!")

    email_body = f"""
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    |
    |
    |
    | Lambda function Error details
    | Lambda function name ::: {lambda_function_name}
    | Log Group ::: {logGroup}
    | Log Stream ::: {logStream}
    | Error message ::: {error_msg}
    |
    |
    |
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """

    email_subject = f"Error details of Lambda function | {lambda_function_name}"

    try:
        sns_client.publish(
            TargetArn=SNS_TOPIC_ARN, Subject=email_subject, Message=email_body
        )
    except ClientError as e:
        logger.error(e)


def lambda_handler(event, context):
    payload = process_event(event)
    (
        logGroup,
        logStream,
        lambda_function_name,
        error_msg,
    ) = process_error_payload(payload)
    send_email(logGroup, logStream, lambda_function_name, error_msg)

    return return_func()
