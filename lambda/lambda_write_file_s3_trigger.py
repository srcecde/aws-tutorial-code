"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""
import boto3
import urllib


def lambda_handler(event, context):
    # Read file from s3
    s3 = boto3.client("s3")
    bucket = "bucket-name"
    key = "filename.txt"
    file = s3.get_object(Bucket=bucket, Key=key)
    paragraph = str(file["Body"].read().decode("utf-8"))

    # Writing back to s3
    with open("/tmp/somefilename.txt", "w") as f:
        f.write(str(paragraph))
    client = boto3.resource("s3")
    client.meta.client.upload_file("/tmp/somefilename.txt", bucket, "somefilename.txt")
    return "Thanks"
