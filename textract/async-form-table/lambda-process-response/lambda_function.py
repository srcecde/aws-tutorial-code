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
from helper.helper import process_response


def lambda_handler(event, context):

    BUCKET_NAME = os.environ["BUCKET_NAME"]

    job_id = json.loads(event["Records"][0]["Sns"]["Message"])["JobId"]
    print(job_id)

    process_response(BUCKET_NAME, job_id, get_table=True, get_kv=True, get_text=True)

    return {"statusCode": 200, "body": json.dumps("File uploaded successfully!")}
