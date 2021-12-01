"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""
import boto3
from urllib.parse import unquote_plus


def lambda_handler(event, context):
    """Read file from s3 on trigger."""
    s3 = boto3.client("s3")
    if event:
        file_obj = event["Records"][0]
        bucketname = str(file_obj["s3"]["bucket"]["name"])
        filename = unquote_plus(str(file_obj["s3"]["object"]["key"]))
        print("Filename: ", filename)
        fileObj = s3.get_object(Bucket=bucketname, Key=filename)
        file_content = fileObj["Body"].read().decode("utf-8")
        print(file_content)
    return "Thanks"
