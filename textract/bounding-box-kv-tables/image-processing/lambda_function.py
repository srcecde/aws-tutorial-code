import asyncio
import logging
import json
import boto3
from urllib.parse import unquote_plus
from helper.helper import process_response


def lambda_handler(event, context):

    textract = boto3.client("textract")
    s3 = boto3.client("s3")
    if event:
        file_obj = event["Records"][0]
        bucketname = str(file_obj["s3"]["bucket"]["name"])
        filename = unquote_plus(str(file_obj["s3"]["object"]["key"]))

        logging.info(f"Bucket: {bucketname} ::: Key: {filename}")

        response = textract.analyze_document(
            Document={
                "S3Object": {
                    "Bucket": bucketname,
                    "Name": filename,
                }
            },
            FeatureTypes=["FORMS", "TABLES"],
        )

        if asyncio.run(process_response(response, s3, bucketname, filename)):
            logging.info("Successfully uploaded processed file!")
            return {
                "statusCode": 200,
                "body": json.dumps("File processed successfully!"),
            }
        else:
            logging.error("Error processing file!")
            return {
                "statusCode": 500,
                "body": json.dumps("Error processing file!"),
            }
