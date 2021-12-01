# -*- coding: utf-8 -*-
__author__ = "Chirag Rathod (Srce Cde)"
__license__ = "MIT"
__email__ = "chiragr83@gmail.com"
__maintainer__ = "Chirag Rathod (Srce Cde)"


import json
import io
from urllib.parse import unquote_plus
import boto3
import pandas as pd


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    s3_resource = boto3.resource("s3")
    if event:
        s3_records = event["Records"][0]
        bucket_name = str(s3_records["s3"]["bucket"]["name"])
        file_name = unquote_plus(str(s3_records["s3"]["object"]["key"]))
        file_obj = s3.get_object(Bucket=bucket_name, Key=file_name)
        file_content = file_obj["Body"].read()

        read_excel_data = io.BytesIO(file_content)

        df = pd.read_excel(read_excel_data)
        df = df.assign(dummy="dummy_value")
        df.to_csv("/tmp/updated.csv")

        s3_resource.Bucket("bucket-name").upload_file("/tmp/updated.csv", "updated.csv")

    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
