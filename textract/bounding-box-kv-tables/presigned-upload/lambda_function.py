import os
import json
import logging
import boto3
from helper.helper import create_presigned_post, process_error


def lambda_handler(event, context):
    try:
        object_name = event["queryStringParameters"]["filename"]
    except Exception as e:
        error_msg = process_error()
        logging.error(error_msg)
        return {"statusCode": 500, "body": json.dumps("Invalid parameter!")}
    s3 = boto3.client("s3")
    try:
        BUCKET_NAME = os.environ["BUCKET_NAME"]
        PREFIX = os.environ["PREFIX"]
        logging.info(f"Destination: {BUCKET_NAME}/{PREFIX}")
    except Exception as e:
        error_msg = process_error()
        logging.error(error_msg)
    return create_presigned_post(s3, BUCKET_NAME, f"{PREFIX}/{object_name}")
