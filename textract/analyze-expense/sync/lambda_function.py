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
import io
import logging
from urllib.parse import unquote_plus
import boto3
import pandas as pd


def upload_to_s3(s3_client, csv_buffer, BUCKET_NAME, key):
    s3_client.put_object(Body=csv_buffer.getvalue(), Bucket=BUCKET_NAME, Key=key)


def extract_lineitems(lineitemgroups, s3_client, BUCKET_NAME, key):
    items, price, row = [], [], []
    for lines in lineitemgroups:
        for item in lines["LineItems"]:
            for line in item["LineItemExpenseFields"]:
                if line.get("Type").get("Text") == "ITEM":
                    items.append(line.get("ValueDetection").get("Text"))
                if line.get("Type").get("Text") == "PRICE":
                    price.append(line.get("ValueDetection").get("Text"))
                if line.get("Type").get("Text") == "EXPENSE_ROW":
                    row.append(line.get("ValueDetection").get("Text"))

    df = pd.DataFrame()
    df["items"] = items
    df["price"] = price
    df["row"] = row
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer)
    upload_to_s3(s3_client, csv_buffer, BUCKET_NAME, key)


def extract_kv(summaryfields, s3_client, BUCKET_NAME, key):
    field_type, label, value = [], [], []
    for item in summaryfields:
        try:
            field_type.append(item.get("Type").get("Text"))
        except:
            field_type.append("")
        try:
            label.append(item.get("LabelDetection", "").get("Text", ""))
        except:
            label.append("")
        try:
            value.append(item.get("ValueDetection", "").get("Text", ""))
        except:
            value.append("")

    df = pd.DataFrame()
    df["Type"] = field_type
    df["Key"] = label
    df["Value"] = value
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer)
    upload_to_s3(s3_client, csv_buffer, BUCKET_NAME, key)


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
        except Exception as e:
            logging.error(e)

        for i in response["ExpenseDocuments"]:
            try:
                extract_kv(
                    i["SummaryFields"], s3_client, bucketname, f"{key}/key_value.csv"
                )
            except Exception as e:
                logging.error(e)
            try:
                extract_lineitems(
                    i["LineItemGroups"], s3_client, bucketname, f"{key}/lineitems.csv"
                )
            except Exception as e:
                logging.error(e)

    return {"statusCode": 200, "body": json.dumps("Hello from Srce Cde!")}
