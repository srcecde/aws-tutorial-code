"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""

import os
import sys
import json
import boto3
import logging
import traceback
from urllib.parse import unquote_plus

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def process_error():
    ex_type, ex_value, ex_traceback = sys.exc_info()
    traceback_string = traceback.format_exception(ex_type, ex_value, ex_traceback)
    error_msg = json.dumps(
        {
            "errorType": ex_type.__name__,
            "errorMessage": str(ex_value),
            "stackTrace": traceback_string,
        }
    )
    return error_msg


try:
    OUTPUT_BUCKET_NAME = os.environ["OUTPUT_BUCKET_NAME"]
    OUTPUT_S3_PREFIX = os.environ["OUTPUT_S3_PREFIX"]
    SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
    SNS_ROLE_ARN = os.environ["SNS_ROLE_ARN"]
    logger.info(
        f"OUTPUT_BUCKET_NAME: {OUTPUT_BUCKET_NAME}, OUTPUT_S3_PREFIX: {OUTPUT_S3_PREFIX}, SNS_TOPIC_ARN: {SNS_TOPIC_ARN}, SNS_ROLE_ARN: {SNS_ROLE_ARN}"
    )
except Exception as e:
    error_msg = process_error()
    logger.error(error_msg)


def lambda_handler(event, context):

    textract = boto3.client("textract")
    try:
        if "Records" in event:
            logger.info(f"Event: {event}")
            file_obj = event["Records"][0]
            bucketname = str(file_obj["s3"]["bucket"]["name"])
            filename = unquote_plus(str(file_obj["s3"]["object"]["key"]))
            logger.info(f"Bucket: {bucketname} ::: Key: {filename}")

            response = textract.start_document_analysis(
                DocumentLocation={"S3Object": {"Bucket": bucketname, "Name": filename}},
                FeatureTypes=[
                    "TABLES",
                    "FORMS",
                ],
                OutputConfig={
                    "S3Bucket": OUTPUT_BUCKET_NAME,
                    "S3Prefix": OUTPUT_S3_PREFIX,
                },
                NotificationChannel={
                    "SNSTopicArn": SNS_TOPIC_ARN,
                    "RoleArn": SNS_ROLE_ARN,
                },
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                logger.info(f"Job created successfully")
                return {
                    "statusCode": 200,
                    "body": json.dumps("Job created successfully!"),
                }
            else:
                logger.error(f"Job creation failed")
                return {
                    "statusCode": 500,
                    "body": json.dumps("Textract failed to parse!"),
                }
    except Exception as e:
        error_msg = process_error()
        logger.error(error_msg)
        return {"statusCode": 500, "body": json.dumps("Invalid trigger event!")}
