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
    s3 = boto3.client("s3")
    if event:
        file_obj = event["Records"][0]
        filename = str(file_obj['s3']['object']['key'])
        filename = urllib.parse.unquote_plus(filename)
        print("Filename: ", filename)
        fileObj = s3.get_object(Bucket = "bucket-name", Key=filename)
        file_content = fileObj["Body"].read().decode('utf-8')
        print(file_content)
	return 'Thanks'
