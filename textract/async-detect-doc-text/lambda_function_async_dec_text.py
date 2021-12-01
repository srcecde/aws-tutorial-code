"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""

import os
import json
import boto3
from urllib.parse import unquote_plus

OUTPUT_BUCKET_NAME = os.environ["OUTPUT_BUCKET_NAME"]
OUTPUT_S3_PREFIX = os.environ["OUTPUT_S3_PREFIX"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
SNS_ROLE_ARN = os.environ["SNS_ROLE_ARN"]


def lambda_handler(event, context):

    textract = boto3.client("textract")
    if event:
        file_obj = event["Records"][0]
        bucketname = str(file_obj["s3"]["bucket"]["name"])
        filename = unquote_plus(str(file_obj["s3"]["object"]["key"]))

        print(f"Bucket: {bucketname} ::: Key: {filename}")

        response = textract.start_document_text_detection(
            DocumentLocation={"S3Object": {"Bucket": bucketname, "Name": filename}},
            OutputConfig={"S3Bucket": OUTPUT_BUCKET_NAME, "S3Prefix": OUTPUT_S3_PREFIX},
            NotificationChannel={"SNSTopicArn": SNS_TOPIC_ARN, "RoleArn": SNS_ROLE_ARN},
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return {"statusCode": 200, "body": json.dumps("Job created successfully!")}
        else:
            return {"statusCode": 500, "body": json.dumps("Job creation failed!")}
