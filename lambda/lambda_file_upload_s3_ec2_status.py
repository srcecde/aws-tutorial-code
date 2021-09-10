# -*- coding: utf-8 -*-
__author__ = "Chirag Rathod (Srce Cde)"
__license__ = "MIT"
__email__ = "chiragr83@gmail.com"
__maintainer__ = "Chirag Rathod (Srce Cde)"


import json
import boto3
from pprint import pprint


def lambda_handler(event, context):
    client = boto3.client("ec2")
    s3 = boto3.client("s3")
    status = client.describe_instance_status(IncludeAllInstances=True)

    with open("/tmp/log.txt", "w") as f:
        json.dump(status, f)

    s3.upload_file("/tmp/log.txt", "layer-release-test", "logs.txt")

    for i in status["InstanceStatuses"]:
        print("AvailabilityZone : ", i["AvailabilityZone"])
        print("InstanceId : ", i["InstanceId"])
        print("Instance State :", i["InstanceState"])
        print("Instance Status : ", i["InstanceStatus"])
        print("System status : ", i["SystemStatus"])
        print("\n")

    return {"statusCode": 200, "body": json.dumps("File uploaded successfully!")}
