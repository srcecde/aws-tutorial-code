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
import json
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)

    bucket_name = os.environ.get("BUCKET_NAME", None)
    try:
        if event and bucket_name:
            s3 = boto3.client("s3")
            user_name = event.get("pathParameters").get("username")
            file_name = event.get("queryStringParameters").get("filename")

            response = s3.generate_presigned_post(
                Bucket=bucket_name,
                Key=f"{user_name}/{file_name}",
                Fields={"Content-Type": "image/jpg"},
                Conditions=[
                    ["starts-with", "$Content-Type", "image/"],
                    ["content-length-range", 0, 10485760],
                ],
                ExpiresIn=3600,
            )

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(response),
            }
    except Exception as e:
        logger.error(e)

    return {"statusCode": 500, "body": json.dumps("Error processing the request!")}
