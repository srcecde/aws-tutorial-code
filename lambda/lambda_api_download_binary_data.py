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
import base64
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)
    try:
        bucket_name = os.environ.get("BUCKET_NAME", None)
        if event and bucket_name:
            s3 = boto3.client("s3")
            folder_name = event.get("pathParameters").get("folder")
            file_name = event.get("queryStringParameters").get("file")

            fileObj = s3.get_object(
                Bucket=bucket_name, Key=f"{folder_name}/{file_name}"
            )
            file_content = fileObj["Body"].read()

            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/pdf",
                    "Content-Disposition": "attachment; filename={}".format(file_name),
                },
                "body": base64.b64encode(file_content),
                "isBase64Encoded": True,
            }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps("Invalid invocation or Bucket name is not defined!"),
            }

    except Exception as e:
        logger.error(e)
        return {"statusCode": 500, "body": json.dumps("Error processing the request!")}
