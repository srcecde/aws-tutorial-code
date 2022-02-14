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
import json
import ast
import boto3
import logging
import traceback

logger = logging.getLogger()
logger.setLevel(logging.ERROR)


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


def notify_recepients(EMAIL_INFO, public_dns="", START_DEMO=False, STOP_DEMO=False):
    client = boto3.client("ses")

    if START_DEMO:
        subject = "Demo instance is running | Information"
        body = """
            Hello Team,
            <br><br>
            The demo instance is running at: {}
            <br><br>
            Thanks
            <br><br>
            Srce Cde
        """.format(
            public_dns
        )

    if STOP_DEMO:
        subject = "Demo instance stopped"
        body = """
            Hello Team,
            <br><br>
            The demo instance is stopped!
            <br><br>
            Thanks
            <br><br>
            Srce Cde
        """

    message = {"Subject": {"Data": subject}, "Body": {"Html": {"Data": body}}}

    response = client.send_email(
        Source=EMAIL_INFO.get("source"),
        Destination={"ToAddresses": EMAIL_INFO.get("recipients")},
        Message=message,
    )


def get_public_dns(ec2_client, INSTANCE_IDS):
    public_dns = []
    while True:
        dns_response = ec2_client.describe_instances(InstanceIds=INSTANCE_IDS)
        for reservations in dns_response["Reservations"]:
            for info in reservations["Instances"]:
                if (
                    info.get("InstanceId") in INSTANCE_IDS
                    and info.get("State").get("Name") == "running"
                ):
                    public_dns.append(f"http://{info.get('PublicDnsName')}")
        if public_dns:
            break
    return public_dns


def lambda_handler(event, context):
    ec2_client = boto3.client("ec2")
    try:
        INSTANCE_IDS = ast.literal_eval(os.environ["INSTANCE_IDS"])
        EMAIL_INFO = ast.literal_eval(os.environ["EMAIL_INFO"])
    except Exception as e:
        error_msg = process_error()
        logger.error(error_msg)
    try:
        for record in event["Records"]:
            body = json.loads(record["Sns"]["Message"])["messageBody"]
            if body == "START_DEMO":
                # logic to START demo instances
                response = ec2_client.start_instances(InstanceIds=INSTANCE_IDS)
                public_dns = get_public_dns(ec2_client, INSTANCE_IDS)
                notify_recepients(
                    EMAIL_INFO, public_dns, START_DEMO=True, STOP_DEMO=False
                )

            elif body == "STOP_DEMO":
                # logic to STOP demo instances
                response = ec2_client.stop_instances(InstanceIds=INSTANCE_IDS)
                notify_recepients(EMAIL_INFO, START_DEMO=False, STOP_DEMO=True)
            else:
                logger.error("No action performed!")
    except Exception as e:
        error_msg = process_error()
        logger.error(error_msg)

    return {"statusCode": 200, "body": json.dumps("Thanks from Srce Cde!")}
