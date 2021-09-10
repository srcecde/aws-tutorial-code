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
import re


def lambda_handler(event, context):
    client = boto3.client("ec2")
    s3 = boto3.client("s3")

    # fetch information about all the instances
    status = client.describe_instances()

    for i in status["Reservations"]:
        instance_details = i["Instances"][0]
        if instance_details["State"]["Name"].lower() in [
            "shutting-down",
            "stopped",
            "stopping",
            "terminated",
        ]:
            print("InstanceId: ", instance_details["InstanceId"])
            print("Launch time: ", instance_details["LaunchTime"])
            print("State change reason: ", instance_details["StateTransitionReason"])
            print(
                "State change Time: ",
                re.findall("\((.*?) *\)", instance_details["StateTransitionReason"]),
            )
            print("\n")

    return {"statusCode": 200, "body": json.dumps("Thanks!")}
