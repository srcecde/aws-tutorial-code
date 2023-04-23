"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""
import os
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    s3_client = boto3.client("s3")

    try:
        BUCKET_NAME = os.environ["BUCKET_NAME"]
    except Exception as e:
        logger.error("ENV variable is not defined")

    if event and BUCKET_NAME:
        logger.info(f"Event: {event}")
        object_name = event.get("queryStringParameters").get("guide")

        try:
            response = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": BUCKET_NAME, "Key": f"guide/{object_name}"},
                ExpiresIn=3600,
            )
        except ClientError as e:
            logging.error(e)
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": "Error processing the request",
            }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": response,
    }
