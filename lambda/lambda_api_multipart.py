# -*- coding: utf-8 -*-
__author__ = "Chirag Rathod (Srce Cde)"
__license__ = "MIT"
__email__ = "chiragr83@gmail.com"
__maintainer__ = "Chirag Rathod (Srce Cde)"

import json
import base64
import boto3
import email


def lambda_handler(event, context):
    s3 = boto3.client("s3")

    # decoding form-data into bytes
    post_data = base64.b64decode(event["body"])
    # fetching content-type
    try:
        content_type = event["headers"]["Content-Type"]
    except:
        content_type = event["headers"]["content-type"]
    # concate Content-Type: with content_type from event
    ct = "Content-Type: " + content_type + "\n"

    # parsing message from bytes
    msg = email.message_from_bytes(ct.encode() + post_data)

    # checking if the message is multipart
    print("Multipart check : ", msg.is_multipart())

    # if message is multipart
    if msg.is_multipart():
        multipart_content = {}
        # retrieving form-data
        for part in msg.get_payload():
            # checking if filename exist as a part of content-disposition header
            if part.get_filename():
                # fetching the filename
                file_name = part.get_filename()
            multipart_content[
                part.get_param("name", header="content-disposition")
            ] = part.get_payload(decode=True)

        # filename from form-data
        file_name = json.loads(multipart_content["Metadata"])["filename"]
        # u uploading file to S3
        s3_upload = s3.put_object(
            Bucket="bucket-name", Key=file_name, Body=multipart_content["file"]
        )

        # on upload success
        return {"statusCode": 200, "body": json.dumps("File uploaded successfully!")}
    else:
        # on upload failure
        return {"statusCode": 500, "body": json.dumps("Upload failed!")}
