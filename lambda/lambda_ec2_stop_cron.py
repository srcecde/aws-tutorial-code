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

# retrieve list of instance ids from ENV variable to skip stopping
INSTANCE_IDS_TO_IGNORE_STOP = ast.literal_eval(
    os.environ.get("INSTANCE_IDS_TO_IGNORE_STOP", "[]")
)


def process_error() -> dict:
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


def fetch_regions() -> list:
    """
    Helper function to retrieve regions

    Returns:
    --------
    regions: list of AWS regions
    """
    ec2_client = boto3.client("ec2")
    try:
        regions = ec2_client.describe_regions()
    except:
        error_msg = process_error()
        logger.error(error_msg)
    return regions["Regions"]


def stop_instances(ec2_client: object, instance_ids: list) -> None:
    """
    Helper function to stop the instances

    Parameters:
    -----------
    ec2_client: boto3 region specific object
    instance_ids: list of instance ids to stop
    """
    try:
        response = ec2_client.stop_instances(InstanceIds=instance_ids, Force=True)
    except:
        error_msg = process_error()
        logger.error(error_msg)


def start_instances(ec2_client: object, instance_ids: list) -> None:
    """
    Helper function to stop the instances

    Parameters:
    -----------
    ec2_client: boto3 region specific object
    instance_ids: list of instance ids to start
    """
    try:
        response = ec2_client.start_instances(InstanceIds=instance_ids)
    except:
        error_msg = process_error()
        logger.error(error_msg)


def get_instance_ids(response: dict, STOP: bool) -> list:
    """
    Parse the instance IDs from response

    Parameters:
    -----------
    response: boto3 describe_instances response
    STOP: Flag to decide type of instance Ids to fetch

    Returns:
    --------
    instance_ids: list of instance ids to stop
    """
    if STOP:
        instance_ids_to_stop = []
        for resp in response.get("Reservations"):
            for instance in resp.get("Instances"):
                if (
                    instance.get("State").get("Name") in ["pending", "running"]
                    and instance["InstanceId"] not in INSTANCE_IDS_TO_IGNORE_STOP
                ):
                    instance_ids_to_stop.append(instance["InstanceId"])
        return instance_ids_to_stop
    else:
        instance_ids_to_start = []
        for resp in response.get("Reservations"):
            for instance in resp.get("Instances"):
                if instance.get("State").get("Name") in ["stopped", "stopping"]:
                    instance_ids_to_start.append(instance["InstanceId"])
        return instance_ids_to_start


def start_stop_instances_across_region(regions: list, STOP=True) -> None:
    """
    Start / Stop the instances across regions

    Parameters:
    -----------
    regions: list of regions to analyze
    STOP: Flag to decide whether to start or stop the instances

    """
    try:
        for region in regions:
            ec2_client = boto3.client("ec2", region_name=region["RegionName"])
            response = ec2_client.describe_instances()

            instance_ids = get_instance_ids(response, STOP)
            if instance_ids and STOP:
                stop_instances(ec2_client, instance_ids)

            if instance_ids and not STOP:
                start_instances(ec2_client, instance_ids)

            while "NextToken" in response:
                response = ec2_client.describe_instances(
                    NextToken=response["NextToken"]
                )
                instance_ids = get_instance_ids(response, STOP)
                if instance_ids and STOP:
                    stop_instances(ec2_client, instance_ids)

                if instance_ids and not STOP:
                    start_instances(ec2_client, instance_ids)

    except:
        error_msg = process_error()
        logger.error(error_msg)


def lambda_handler(event, context):
    """
    Main handler
    """
    logging.info(event)
    # retrieve regions
    regions = fetch_regions()

    try:
        rule_type = event["resources"][0].split("/")[-1]

        # checking which rule triggered the lambda function
        if "ScheduledEC2StopRule" in rule_type:
            start_stop_instances_across_region(regions, STOP=True)

        if "ScheduledEC2StartRule" in rule_type:
            start_stop_instances_across_region(regions, STOP=False)
    except:
        error_msg = process_error()
        logger.error(error_msg)

    return {"statusCode": 200, "body": json.dumps("Thanks from Srce Cde (Chirag)!")}
