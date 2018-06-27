"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""
import boto3, json
def lambda_handler(event, context):
	#change region_name as per the destination lambda function region
    invokeLam = boto3.client("lambda", region_name="us-east-2")
    payload = {"message": "Hi, you have been invoked."}

    #For InvocationType = "RequestResponse"
    resp = invokeLam.invoke(FunctionName = "lambda_fucntion2", InvocationType = "RequestResponse", Payload = json.dumps(payload))
    print(resp["Payload"].read())

    #For InvocationType = "Event"
    resp = invokeLam.invoke(FunctionName = "lambda_fucntion2", InvocationType = "Event", Payload = json.dumps(payload))
    return 'Thanks'
