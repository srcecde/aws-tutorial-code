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
from ipaddress import ip_network, ip_address


def check_ip(IP_ADDRESS, IP_RANGE):
    VALID_IP = False
    cidr_blocks = list(filter(lambda element: "/" in element, IP_RANGE))
    if cidr_blocks:
        for cidr in cidr_blocks:
            net = ip_network(cidr)
            VALID_IP = ip_address(IP_ADDRESS) in net
            if VALID_IP:
                break
    if not VALID_IP and IP_ADDRESS in IP_RANGE:
        VALID_IP = True

    return VALID_IP


def return_func(
    status_code=200,
    message="Invocation successful!",
    headers={"Content-Type": "application/json"},
    isBase64Encoded=False,
):
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps({"message": message}),
        "isBase64Encoded": isBase64Encoded,
    }


def lambda_handler(event, context):
    IP_ADDRESS = event["requestContext"]["http"]["sourceIp"]
    IP_RANGE = ast.literal_eval(os.environ.get("IP_RANGE", "[]"))
    METHOD = event["requestContext"]["http"]["method"]

    if not IP_RANGE:
        return return_func(status_code=500, message="Unauthorized")

    VALID_IP = check_ip(IP_ADDRESS, IP_RANGE)

    if not VALID_IP:
        return return_func(status_code=500, message="Unauthorized")

    if METHOD == "GET":
        return return_func(status_code=200, message="GET method invoked!")

    if METHOD == "POST":
        return return_func(status_code=200, message="POST method invoked!")

    return return_func()
