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

    # retrieving data from event
    get_file_content = event["content"]

    # decoding data
    decode_content = base64.b64decode(get_file_content)

    # uploading file to S3 bucket
    s3_upload = s3.put_object(Bucket="bucket-name", Key="file.pdf", Body=decode_content)

    return {"statusCode": 200, "body": json.dumps("Thanks for using!")}
