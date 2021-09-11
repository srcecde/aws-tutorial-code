"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""

import boto3
from pprint import pprint


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    bucket = "bucket-name"
    key = "filename.txt"
    file = s3.get_object(Bucket=bucket, Key=key)
    paragraph = str(file["Body"].read())

    comprehend = boto3.client("comprehend")

    # Extracting sentiments using comprehend
    sentiment = comprehend.detect_sentiment(Text=paragraph, LanguageCode="en")
    print(sentiment)

    # Extracting entities using comprehend
    entities = comprehend.detect_entities(Text=paragraph, LanguageCode="en")
    pprint(entities)

    # Extracting keyphrase using comprehend
    keyphrase = comprehend.detect_key_phrases(Text=paragraph, LanguageCode="en")
    pprint(keyphrase)

    return "Thanks"
