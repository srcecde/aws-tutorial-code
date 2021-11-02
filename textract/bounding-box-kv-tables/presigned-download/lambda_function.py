import os
import json
import logging
import boto3
from helper.helper import process_error, create_presigned_url, check_file_exists


def lambda_handler(event, context):
    try:
        object_name = event["queryStringParameters"]["filename"]
    except Exception as e:
        error_msg = process_error()
        logging.error(error_msg)
        return {"statusCode": 500, "body": json.dumps("Invalid parameter!")}
    s3 = boto3.client("s3")
    BUCKET_NAME, PREFIX, FILE_PATH = None, None, None
    try:
        BUCKET_NAME = os.environ["BUCKET_NAME"]
        PREFIX = os.environ["PREFIX"]
        FILE_PATH = f"{PREFIX}/{object_name}"
        logging.info(f"Destination: {BUCKET_NAME}/{PREFIX}")
    except Exception as e:
        error_msg = process_error()
        logging.error(error_msg)

    if check_file_exists(s3, BUCKET_NAME, FILE_PATH):
        return create_presigned_url(s3, BUCKET_NAME, FILE_PATH)
    else:
        return {"statusCode": 404, "body": json.dumps("File is being processd!")}
