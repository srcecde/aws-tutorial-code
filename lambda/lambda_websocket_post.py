# -*- coding: utf-8 -*-
__author__ = "Chirag Rathod (Srce Cde)"
__license__ = "MIT"
__email__ = "chiragr83@gmail.com"
__maintainer__ = "Chirag Rathod (Srce Cde)"

import json
import boto3

# connection URL (i.e. backend URL)
URL = "connection-url"
gatewayapi = boto3.client("apigatewaymanagementapi", endpoint_url=URL)


def lambda_handler(event, context):
    # fetching connectionId from event
    connectionId = event["requestContext"].get("connectionId")

    # loading JSON message
    msg = json.loads(event["body"])

    # check if message key exist in payload
    if "message" in msg:
        # fetching client message
        msg = msg["message"]

        if msg.lower() == "hello":
            # response from server
            r_msg = "Hello from server!"
            # posts message to connected client
            post_message(connectionId, r_msg)
            # return statuscode
            return {"statusCode": 200}

        elif msg.lower() == "how are you":
            r_msg = "Server is fine! How are you?"
            post_message(connectionId, r_msg)
            return {"statusCode": 200}

        elif msg.lower() == "good":
            r_msg = "Great! It's nice talking to you"
            post_message(connectionId, r_msg)
            # closing the connection from server
            response = gatewayapi.delete_connection(ConnectionId=connectionId)
            return {"statusCode": 200}
        else:
            r_msg = "Thanks!"
            post_message(connectionId, r_msg)
            # closing the connection from server
            response = gatewayapi.delete_connection(ConnectionId=connectionId)
            return {"statusCode": 200}
    else:
        # handling if message does not exist
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Message does not exist!"}),
        }


def post_message(connectionId, msg):
    gateway_resp = gatewayapi.post_to_connection(
        ConnectionId=connectionId, Data=json.dumps({"message": msg})
    )
