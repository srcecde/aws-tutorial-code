"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""

import json
import boto3
import datetime


def lambda_handler(event, context):
    # delete IAM user based on password last used

    client = boto3.client("iam")
    today = datetime.datetime.now()
    data = client.list_users()

    for i in data["Users"]:
        days = (today - i["PasswordLastUsed"].replace(tzinfo=None)).days
        username = i["UserName"]
        if days > 60:
            client.delete_user(UserName=username)

    return {"statusCode": 200, "body": json.dumps("Thanks!")}
