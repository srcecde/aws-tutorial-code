"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""

import sys
import boto3
import io
import logging
import traceback
import json
from .parser import Parse
import pandas as pd

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def process_error():
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


def upload_to_s3(csv_buffer, BUCKET_NAME, key):
    client = boto3.client("s3")
    client.put_object(Body=csv_buffer.getvalue(), Bucket=BUCKET_NAME, Key=key)


def extract_kv(final_map):
    keys, values = [], []
    for i in final_map:
        for k, v in i.items():
            keys.append(k)
            values.append(v)
    return keys, values


def save_kv_csv(keys, values, job_id, BUCKET_NAME):
    key = f"kv/{job_id}/key_value.csv"
    df = pd.DataFrame()
    df["Keys"] = keys
    df["Values"] = values
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer)
    upload_to_s3(csv_buffer, BUCKET_NAME, key)


def extract_kv_text(text):
    keys, values = [], []
    for k, v in text.items():
        keys.append(k)
        values.append(v)
    return keys, values


def save_table_csv(table, job_id, BUCKET_NAME):
    for i, j in table.items():
        for k, v in j.items():
            csv_buffer = io.StringIO()
            df = pd.DataFrame(v)
            df.columns = df.iloc[0]
            df = df[1:]
            df.to_csv(csv_buffer)
            key = f"tables/{job_id}/{k}.csv"
            upload_to_s3(csv_buffer, BUCKET_NAME, key)


def save_text_csv(keys, values, job_id, BUCKET_NAME):
    key = f"text/{job_id}/text.csv"
    df = pd.DataFrame()
    df["PageNo"] = keys
    df["Text"] = values
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer)
    upload_to_s3(csv_buffer, BUCKET_NAME, key)


def process_response(BUCKET_NAME, job_id, get_table=True, get_kv=True, get_text=True):
    textract = boto3.client("textract")

    response = {}
    pages = []

    logging.info("Fetching response")
    response = textract.get_document_analysis(JobId=job_id)

    pages.append(response)

    nextToken = None
    logging.info("Checking paginated response")
    if "NextToken" in response:
        logging.info("Paginated response found")
        nextToken = response["NextToken"]

    while nextToken:
        response = textract.get_document_analysis(JobId=job_id, NextToken=nextToken)
        pages.append(response)
        nextToken = None
        if "NextToken" in response:
            nextToken = response["NextToken"]

    keys, values = [], []
    text_key, text_value = [], []
    logger.info("Looping through pages & parsing the response")
    for page in pages:
        parse = Parse(page=page, get_table=True, get_kv=True, get_text=True)
        table, final_map, text = parse.process_response()

        if get_table:
            save_table_csv(table, job_id, BUCKET_NAME)

        if get_kv:
            k, v = extract_kv(final_map)
            keys.extend(k)
            values.extend(v)

        if get_text:
            k, v = extract_kv_text(text)
            text_key.extend(text)
            text_value.extend(v)
    if get_kv:
        save_kv_csv(keys, values, job_id, BUCKET_NAME)
    if get_text:
        save_text_csv(text_key, text_value, job_id, BUCKET_NAME)
    logger.info("Parsing completed")
