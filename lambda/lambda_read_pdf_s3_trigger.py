# -*- coding: utf-8 -*-
__author__ = "Chirag Rathod (Srce Cde)"
__license__ = "MIT"
__email__ = "chiragr83@gmail.com"
__maintainer__ = "Chirag Rathod (Srce Cde)"

import json
import boto3
from urllib.parse import unquote_plus
import fitz


def lambda_handler(event, context):
    """Read file from s3 on trigger."""
    # boto3 client
    s3 = boto3.client("s3")
    if event:
        file_obj = event["Records"][0]
        # fetching bucket name from event
        bucketname = str(file_obj["s3"]["bucket"]["name"])
        # fetching file name from event
        filename = unquote_plus(str(file_obj["s3"]["object"]["key"]))
        # retrieving object from S3
        fileObj = s3.get_object(Bucket=bucketname, Key=filename)
        # reading botocore stream
        file_content = fileObj["Body"].read()

        # loading pdf from memory/stream
        with fitz.open(stream=file_content, filetype="pdf") as doc:
            text = ""
            # iterating through pdf file pages
            for page in doc:
                # fetching & appending text to text variable of each page
                text += page.getText()

        print(text)
    return {"statusCode": 200, "body": json.dumps("Thanks from Srce Cde!")}
