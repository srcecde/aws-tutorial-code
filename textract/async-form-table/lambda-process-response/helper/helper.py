"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""

import sys
from collections import ChainMap
import boto3
import io
import logging
import traceback
import json
import pandas as pd
from operator import itemgetter
from .parser import Parse


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


def map_word_id(response):
    word_map = {}
    for block in response["Blocks"]:
        if block["BlockType"] == "WORD":
            word_map[block["Id"]] = block["Text"]
        if block["BlockType"] == "SELECTION_ELEMENT":
            word_map[block["Id"]] = block["SelectionStatus"]
    return word_map


def process_response(BUCKET_NAME, job_id, get_table=True, get_kv=True, get_text=True):
    textract = boto3.client("textract")

    response = {}
    pages = []

    logging.info("Fetching response")
    response = textract.get_document_analysis(JobId=job_id)
    print(type(response))
    pages.append(response)

    nextToken = None
    logging.info("Checking paginated response")
    if "NextToken" in response:
        logging.info("Paginated response found")
        nextToken = response["NextToken"]

    while nextToken:
        response = textract.get_document_analysis(JobId=job_id, NextToken=nextToken)
        print(type(response))
        pages.append(response)
        print("NEXTTOKN")
        nextToken = None
        if "NextToken" in response:
            nextToken = response["NextToken"]
        print(nextToken)

    keys, values = [], []
    text_key, text_value = [], []
    logger.info("Looping through pages & parsing the response")
    pages_block = []
    for page in pages:
        pages_block.extend(page["Blocks"])

    parse = Parse(
        page=pages_block, get_table=get_table, get_kv=get_kv, get_text=get_text
    )
    table, final_map, text = parse.process_response()

    if get_kv:
        keys = list(map(itemgetter(0), final_map))
        values = list(map(itemgetter(1), final_map))
        save_kv_csv(keys, values, job_id, BUCKET_NAME)
    if get_table:
        save_table_csv(table, job_id, BUCKET_NAME)
    if get_text:
        k, v = extract_kv_text(text)
        text_key.extend(text)
        text_value.extend(v)
        save_text_csv(text_key, text_value, job_id, BUCKET_NAME)
    logger.info("Parsing completed")
