"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""
import sys
import traceback
import logging
import json
import uuid
import boto3
from urllib.parse import unquote_plus

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def process_error() -> dict:
    ex_type, ex_value, ex_traceback = sys.exc_info()
    traceback_string = traceback.format_exception(ex_type, ex_value, ex_traceback)
    error_msg = json.dumps(
        {
            "errorType": ex_type.__name__,
            "errorMessage": str(ex_value),
            "stackTrace": traceback_string,
        }
    )
    return error_msg


def extract_text(response: dict, extract_by="LINE") -> list:
    text = []
    for block in response["Blocks"]:
        if block["BlockType"] == extract_by:
            text.append(block["Text"])
    return text


def lambda_handler(event, context):
    textract = boto3.client("textract")
    s3 = boto3.client("s3")

    try:
        if "Records" in event:
            file_obj = event["Records"][0]
            bucketname = str(file_obj["s3"]["bucket"]["name"])
            filename = unquote_plus(str(file_obj["s3"]["object"]["key"]))

            logging.info(f"Bucket: {bucketname} ::: Key: {filename}")

            response = textract.detect_document_text(
                Document={
                    "S3Object": {
                        "Bucket": bucketname,
                        "Name": filename,
                    }
                }
            )
            logging.info(json.dumps(response))

            # change LINE by WORD if you want word level extraction
            raw_text = extract_text(response, extract_by="LINE")
            logging.info(raw_text)

            s3.put_object(
                Bucket=bucketname,
                Key=f"output/{filename.split('/')[-1]}_{uuid.uuid4().hex}.txt",
                Body=str("\n".join(raw_text)),
            )

            return {
                "statusCode": 200,
                "body": json.dumps("Document processed successfully!"),
            }
    except:
        error_msg = process_error()
        logger.error(error_msg)

    return {"statusCode": 500, "body": json.dumps("Error processing the document!")}
