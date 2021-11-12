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
import logging
from helper.helper import process_response, process_error

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    try:
        BUCKET_NAME = os.environ["BUCKET_NAME"]
        logger.info(f"Destination bucket: {BUCKET_NAME}")
    except Exception as e:
        error_msg = process_error()
        logger.error(error_msg)

    try:
        if "Records" in event:
            logger.info(f"Event: {event}")
            job_id = json.loads(event["Records"][0]["Sns"]["Message"])["JobId"]
            logger.info(f"JobId: {job_id}")

            logger.info("Parsing initiated")
            process_response(
                BUCKET_NAME, job_id, get_table=True, get_kv=True, get_text=True
            )

            return {
                "statusCode": 200,
                "body": json.dumps("File uploaded successfully!"),
            }
    except Exception as e:
        error_msg = process_error()
        logger.error(error_msg)
        return {"statusCode": 500, "body": json.dumps("Error parsing the response!")}
