import sys
import io
import json
import traceback
import pandas as pd


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
