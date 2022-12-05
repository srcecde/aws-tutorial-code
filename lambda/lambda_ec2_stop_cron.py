"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""

import os
import sys
import traceback
import logging
import ast
import json
import boto3

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


def fetch_regions():
    ec2_client = boto3.client("ec2")
    regions = ec2_client.describe_regions()
    return regions["Regions"]


def stop_instances(ec2_client, instance_ids):
    try:
        response = ec2_client.stop_instances(InstanceIds=instance_ids, Force=True)
    except:
        error_msg = process_error()
        logger.error(error_msg)


def describe_instances(ec2_client, response, INSTANCE_IDS_TO_IGNORE):
    instance_ids_to_stop = []
    for resp in response.get("Reservations"):
        for instance in resp.get("Instances"):
            if (
                instance.get("State").get("Name") in ["pending", "running"]
                and instance["InstanceId"] not in INSTANCE_IDS_TO_IGNORE
            ):
                instance_ids_to_stop.append(instance["InstanceId"])
    return instance_ids_to_stop


def instance_ids_to_stop(regions, INSTANCE_IDS_TO_IGNORE):
    for region in regions:
        ec2_client = boto3.client("ec2", region_name=region["RegionName"])
        response = ec2_client.describe_instances()

        instance_ids = describe_instances(ec2_client, response, INSTANCE_IDS_TO_IGNORE)
        stop_instances(ec2_client, instance_ids)

        while "NextToken" in response:
            response = ec2_client.describe_instances(NextToken=response["NextToken"])
            instance_ids = describe_instances(
                ec2_client, response, INSTANCE_IDS_TO_IGNORE
            )
            stop_instances(ec2_client, instance_ids)


def lambda_handler(event, context):
    INSTANCE_IDS_TO_IGNORE = ast.literal_eval(
        os.environ.get("INSTANCE_IDS_TO_IGNORE", "[]")
    )

    regions = fetch_regions()
    instance_ids_to_stop(regions, INSTANCE_IDS_TO_IGNORE)

    return {"statusCode": 200, "body": json.dumps("Thanks from Srce Cde (Chirag)!")}
