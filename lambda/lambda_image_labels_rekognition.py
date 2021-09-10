"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""
import boto3


def lambda_handler(event, context):

    client = boto3.client("rekognition")
    s3 = boto3.client("s3")

    # reading file from s3 bucket and passing it as bytes
    fileObj = s3.get_object(Bucket="bucket-name", Key="obj_scene.jpeg")
    file_content = fileObj["Body"].read()

    # passing bytes data
    response = client.detect_labels(
        Image={"Bytes": file_content}, MaxLabels=3, MinConfidence=70
    )

    # passing s3 bucket object file reference
    response = client.detect_labels(
        Image={"S3Object": {"Bucket": "bucket-name", "Name": "filename"}},
        MaxLabels=3,
        MinConfidence=70,
    )

    print(response)

    return "Thanks"
