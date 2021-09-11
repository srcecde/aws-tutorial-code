"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""
import boto3


def datachunk(para):
    text_list = []
    while para:
        text_list.append(str(para[:4700]))
        para = para[4700:]
    return text_list[:25]


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    bucket = "bucket-name"
    key = "filename.txt"
    file = s3.get_object(Bucket=bucket, Key=key)
    paragraph = str(file["Body"].read().decode("utf-8"))
    comprehend = boto3.client("comprehend")

    sentiment = comprehend.batch_detect_sentiment(
        TextList=datachunk(paragraph), LanguageCode="en"
    )
    print(sentiment)

    entities = comprehend.batch_detect_entities(
        TextList=datachunk(paragraph), LanguageCode="en"
    )
    print(entities)

    keyphrase = comprehend.batch_detect_key_phrases(
        TextList=datachunk(paragraph), LanguageCode="en"
    )
    print(keyphrase)

    return "Thanks"
