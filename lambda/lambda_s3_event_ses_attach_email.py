"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def lambda_handler(event, context):
    
    ses = boto3.client("ses")
    s3 = boto3.client("s3")

    for i in event["Records"]:
        action = i["eventName"]
        ip = i["requestParameters"]["sourceIPAddress"]
        bucket_name = i["s3"]["bucket"]["name"]
        object = i["s3"]["object"]["key"]

    fileObj = s3.get_object(Bucket = bucket_name, Key = object)
    file_content = fileObj["Body"].read()

    sender = "mail@mail.com"
    to = "mail@mail.com"
    subject = str(action) + 'Event from ' + bucket_name
    body = """
        <br>
        This email is to notify you regarding {} event.
        The object {} is uploaded.
        Source IP: {}
    """.format(action, object, ip)

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to

    body_txt = MIMEText(body, "html")

    attachment = MIMEApplication(file_content)
    attachment.add_header("Content-Disposition", "attachment", filename=object)

    msg.attach(body_txt)
    msg.attach(attachment)

    response = ses.send_raw_email(Source = sender, Destinations = [to], RawMessage = {"Data": msg.as_string()})
    
    return "Thanks"
