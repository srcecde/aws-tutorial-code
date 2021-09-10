"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""

# importing AWS SDK for Python
import json
import boto3


def lambda_handler(event, context):
    client = boto3.client("ec2")
    s3 = boto3.client("s3")

    # fetching EC2 instance state and status check information
    status = client.describe_instance_status(IncludeAllInstances=True)

    # Writing data to S3 bucket (text file)
    s3.put_object(Bucket="bucket-name", Key="data-log.txt", Body=str(status))

    # for ex. while dealing with json or any other file type, need to pass the ContentType parameter
    # s3.put_object(Bucket = "bucket-name", Key = "data-log.json", Body = str(status), ContentType = "application/json")

    return {"statusCode": 200, "body": json.dumps("Thanks!")}
