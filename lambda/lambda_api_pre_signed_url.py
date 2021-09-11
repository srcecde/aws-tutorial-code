# -*- coding: utf-8 -*-
__author__ = "Chirag Rathod (Srce Cde)"
__license__ = "MIT"
__email__ = "chiragr83@gmail.com"
__maintainer__ = "Chirag Rathod (Srce Cde)"

import json
import base64
import boto3


def lambda_handler(event, context):
    s3 = boto3.client("s3")

    # For fetching bucket_name & file_name using proxy integration method from API Gateway
    bucket_name = event["pathParameters"]["bucket"]
    file_name = event["queryStringParameters"]["file"]

    # For fetching bucket_name & file_name using legacy method from API Gateway
    bucket_name = event["params"]["path"]["bucket"]
    file_name = event["params"]["querystring"]["file"]

    """
    1. Generate pre-signed URL for downloading file
    2. Replace get_object with put_object for generating pre-signed URL to upload file
    3. Use PUT method while uploading file using Pre-Signed URL
    """
    URL = s3.generate_presigned_url(
        "get_object", Params={"Bucket": bucket_name, "Key": file_name}, ExpiresIn=3600
    )

    """
    1. Generate pre-signed URL for downloading file
    2. Use POST method while uploading file using Pre-Signed URL
    """
    URL = s3.generate_presigned_post(
        Bucket=bucket_name, Key=file_name, Fields=None, Conditions=None, ExpiresIn=3600
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"URL": URL}),
    }
