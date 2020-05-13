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
    status = client.describe_instance_status(IncludeAllInstances = True)
    
    # fetch all instance ids
    instance_ids = [i["InstanceId"] for i in status["InstanceStatuses"]]
    
    # fetch information about all the instances
    status = client.describe_instances(InstanceIds=instance_ids)
    
    for i in status["Reservations"]:
        st = i['Instances'][0]
        if st["State"]["Name"].lower() == "stopped":
            print("InstanceId: ", st["InstanceId"])
            print("Stopped Time: ", re.findall('\((.*?) *\)', st["StateTransitionReason"]))
    
    return {
        'statusCode': 200,
        'body': json.dumps('Thanks!')
    }
