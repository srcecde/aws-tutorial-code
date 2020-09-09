#-*- coding: utf-8 -*-
__author__ = "Chirag Rathod (Srce Cde)"
__license__ = "MIT"
__email__ = "chiragr83@gmail.com"
__maintainer__ = "Chirag Rathod (Srce Cde)"

import time
import json
import boto3

def lambda_handler(event, context):

    # boto3 client
    client = boto3.client('ec2')
    ssm = boto3.client('ssm')
    
    # getting instance information
    describeInstance = client.describe_instances()

    InstanceId=[]
    # fetchin public IP address of the running instances
    for i in describeInstance['Reservations']:
        for instance in i['Instances']:
            if instance["State"]["Name"] == "running":
                InstanceId.append(instance['InstanceId'])

    for instanceid in InstanceId:
        response = ssm.send_command(
                InstanceIds=[instanceid],
                DocumentName="AWS-RunShellScript",
                Parameters={'commands': ['command_to_be_executed']}, )

        command_id = response['Command']['CommandId']
        
        time.sleep(3)
        
        output = ssm.get_command_invocation(
              CommandId=command_id,
              InstanceId=instanceid
            )
        print(output)

    return {
        'statusCode': 200,
        'body': json.dumps('Thanks from Srce Cde!')
    }
