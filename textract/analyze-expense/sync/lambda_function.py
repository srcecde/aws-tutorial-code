"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""

import json
import uuid
import logging
from urllib.parse import unquote_plus
import boto3
from helper.helper import process_error, extract_kv, extract_lineitems


def lambda_handler(event, context):
    textract = boto3.client("textract")
    s3_client = boto3.client("s3")
    if event:
        file_obj = event["Records"][0]
        bucketname = str(file_obj["s3"]["bucket"]["name"])
        filename = unquote_plus(str(file_obj["s3"]["object"]["key"]))
        filename.split("/")[-1].split(".")[0]
        key = f"analyze-expense-output/{filename.split('/')[-1].split('.')[0]}_{uuid.uuid4().hex}"

        try:
            response = textract.analyze_expense(
                Document={
                    "S3Object": {
                        "Bucket": bucketname,
                        "Name": filename,
                    }
                }
            )
            print(json.dumps(response))
            for i in response["ExpenseDocuments"]:
                try:
                    extract_kv(
                        i["SummaryFields"],
                        s3_client,
                        bucketname,
                        f"{key}/key_value.csv",
                    )
                except Exception as e:
                    error_msg = process_error()
                    logging.error(error_msg)
                try:
                    extract_lineitems(
                        i["LineItemGroups"],
                        s3_client,
                        bucketname,
                        f"{key}/lineitems.csv",
                    )
                except Exception as e:
                    error_msg = process_error()
                    logging.error(error_msg)

        except Exception as e:
            logging.error(e)

    return {"statusCode": 200, "body": json.dumps("Hello from Srce Cde!")}
