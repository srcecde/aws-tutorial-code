"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""
import os
import ast
import json
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

ses = boto3.client("ses")
s3 = boto3.client("s3")

"""
Set SENDER_EMAIL & TO_EMAILS as the lambda environment variables
For example:
SENDER_EMAIL : email
TO_EMAILS : ['email1', 'email2']
"""
SENDER_EMAIL = os.environ["SENDER_EMAIL"]
TO_EMAILS = ast.literal_eval(os.environ["TO_EMAILS"])


def send_email(sender, receiver, subject, body, file_content, file_name):
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ",".join(receiver)

    body_txt = MIMEText(body, "html")

    attachment = MIMEApplication(file_content)
    attachment.add_header("Content-Disposition", "attachment", filename=file_name)

    msg.attach(body_txt)
    msg.attach(attachment)

    response = ses.send_raw_email(
        Source=sender, Destinations=receiver, RawMessage={"Data": msg.as_string()}
    )

    return response


def lambda_handler(event, context):
    if "Records" in event:
        records = event["Records"][0]
        action = records["eventName"]
        ip = records["requestParameters"]["sourceIPAddress"]
        bucket_name = records["s3"]["bucket"]["name"]
        file_object = records["s3"]["object"]["key"]

        fileObj = s3.get_object(Bucket=bucket_name, Key=file_object)
        file_content = fileObj["Body"].read()
        file_name = file_object.split("/")[-1]

        subject = f"{str(action)} Event from {bucket_name}"
        body = """
            <br>
            This email is to notify you regarding {} event.
            The object {} is Uploaded.
            Source IP: {}
        """.format(
            action, object, ip
        )

        response = send_email(
            SENDER_EMAIL, TO_EMAILS, subject, body, file_content, file_name
        )

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return {"statusCode": 200, "body": json.dumps("Email sent successfully!")}

    return {"statusCode": 500, "body": json.dumps("Email delivery failed!")}
