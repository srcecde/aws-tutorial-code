# -*- coding: utf-8 -*-
__author__ = "Chirag Rathod (Srce Cde)"
__license__ = "MIT"
__email__ = "chiragr83@gmail.com"
__maintainer__ = "Chirag Rathod (Srce Cde)"

import json
import boto3


def sendMessage(eventDetails, subject=None, message=None):
    """Helper method to send message"""

    # configure subject
    if subject:
        subject = subject
    else:
        subject = "S3 Public permission Alert for {} bucket".format(
            eventDetails.get("bucketName")
        )

    # configure message
    if message:
        message = message
    else:
        message = f"""
              The bucket permission is modified. Details below.
              
              UserType : {eventDetails.get('UserType')}
              eventTime : {eventDetails.get('eventTime')}
              region : {eventDetails.get('region')}
              sourceIP: {eventDetails.get('sourceIP')}
              userAgent: {eventDetails.get('userAgent')}
              Other crucial information: {eventDetails.get('parameters')}
              """
    sns = boto3.client("sns")
    # send message
    response = sns.publish(
        TopicArn="arn:aws:sns:us-east-1:052674914236:xxx",
        Message=message,
        Subject=subject,
    )


def getEventDetails(eventData):
    """Helper method to parse event data"""
    eventDetails = {
        "UserType": userDetails(eventData.get("userIdentity")),
        "eventTime": eventData.get("eventTime"),
        "region": eventData.get("awsRegion"),
        "sourceIP": eventData.get("sourceIPAddress"),
        "userAgent": eventData.get("userAgent"),
        "parameters": eventData.get("requestParameters"),
        "bucketName": eventData.get("requestParameters").get("bucketName"),
    }
    return eventDetails


def userDetails(userData):
    """Helper method to parse userdata"""
    if userData.get("type") == "Root":
        userType = "Root User"
    elif userData.get("type") == "IAMUser":
        userType = "IAM User"
    elif userData.get("type") == "AssumedRole":
        userType = "Assumed Role"
    elif userData.get("type") == "FederatedUser":
        userType = "Federated User"
    elif userData.get("type") == "AWSAccount":
        userType = "User from another AWS account"
    elif userData.get("type") == "AWSService":
        userType = "AWS Service"
    return userType


def lambda_handler(event, context):
    """Lambda handler"""
    print(event)
    # parsing event
    eventData = event.get("detail")
    # URI for all user group
    allUserGroup = "http://acs.amazonaws.com/groups/global/AllUsers"
    # URI for auth user group
    authUserGroup = "http://acs.amazonaws.com/groups/global/AuthenticatedUsers"
    # parsing and fetching required information
    eventDetails = getEventDetails(eventData)
    # check for PutBucketPublicAccessBlock eventype
    if eventData.get("eventName") == "PutBucketPublicAccessBlock":
        # fetch information of PutBucketPublicAccessBlock flags
        getPublicInfo = eventData.get("requestParameters").get(
            "PublicAccessBlockConfiguration"
        )
        # checking flags if any is false
        if not (
            getPublicInfo.get("RestrictPublicBuckets")
            and getPublicInfo.get("RestrictPublicBuckets")
            and getPublicInfo.get("RestrictPublicBuckets")
            and getPublicInfo.get("RestrictPublicBuckets")
        ):
            # sending message/email
            sendMessage(eventDetails, subject=None, message=None)

    # check for PutBucketAcl eventype
    if eventData.get("eventName") == "PutBucketAcl":
        # fetching grant information
        grantDetails = (
            eventData.get("requestParameters")
            .get("AccessControlPolicy")
            .get("AccessControlList")
            .get("Grant")
        )
        # setting flag
        flag = False
        # checking length of grant since grantDetails[0] will be for owner
        if len(grantDetails) > 1:
            # looping through grants. Skipping first since its for owner itself
            for grant in grantDetails[1:]:
                # checking the user group
                if grant.get("Grantee").get("URI") and (
                    grant.get("Grantee").get("URI") in [allUserGroup, authUserGroup]
                ):
                    # checking if any of this permission exist
                    if grant.get("Permission") in [
                        "READ",
                        "WRITE",
                        "READ_ACP",
                        "WRITE_ACP",
                        "FULL_CONTROL",
                    ]:
                        # setting flag true
                        flag = True

        # if flag is true then send message
        if flag:
            sendMessage(eventDetails, subject=None, message=None)

    # check for CreateBucket eventype
    if eventData.get("eventName") == "CreateBucket":
        # create client of S3
        client = boto3.client("s3")
        # setting put_public_access_block to True
        r = client.put_public_access_block(
            Bucket=eventDetails.get("bucketName"),
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True,
            },
        )

    return {"statusCode": 200, "body": json.dumps("Thanks from Srce Cde!")}
