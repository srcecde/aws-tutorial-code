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
import uuid
from urllib.parse import unquote_plus
import boto3


def lambda_handler(event, context):
    textract = boto3.client("textract")
    FLOW_ARN = os.environ["FLOW_ARN"]
    if event:
        file_obj = event["Records"][0]
        bucketname = str(file_obj["s3"]["bucket"]["name"])
        filename = unquote_plus(str(file_obj["s3"]["object"]["key"]))

        response = textract.analyze_document(
            Document={
                "S3Object": {
                    "Bucket": bucketname,
                    "Name": filename,
                }
            },
            FeatureTypes=["FORMS"],
            HumanLoopConfig={
                "HumanLoopName": uuid.uuid4().hex,
                "FlowDefinitionArn": FLOW_ARN,
                "DataAttributes": {
                    "ContentClassifiers": [
                        "FreeOfPersonallyIdentifiableInformation",
                        "FreeOfAdultContent",
                    ]
                },
            },
        )
        print(json.dumps(response))

        return {
            "statusCode": 200,
            "body": json.dumps("Document processed successfully!"),
        }

    return {"statusCode": 500, "body": json.dumps("Issue processing file!")}
