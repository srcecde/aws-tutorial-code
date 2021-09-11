# -*- coding: utf-8 -*-
__author__ = "Chirag Rathod (Srce Cde)"
__license__ = "MIT"
__email__ = "chiragr83@gmail.com"
__maintainer__ = "Chirag Rathod (Srce Cde)"


import json
import boto3


s3 = boto3.client("s3")
comprehend = boto3.client("comprehend")


def lambda_handler(event, context):
    if event:
        s3_object = event["Records"][0]["s3"]
        bucket_name = s3_object["bucket"]["name"]
        file_name = s3_object["object"]["key"]
        file_obj = s3.get_object(Bucket=bucket_name, Key=file_name)
        transcript_result = json.loads(file_obj["Body"].read())
        paragraph = transcript_result["results"]["transcripts"][0]["transcript"]

        response = comprehend.batch_detect_sentiment(
            TextList=data_chunk(paragraph), LanguageCode="en"
        )

        final_response = average_sentiment(response)

        s3.put_object(Bucket="bucket-name", Key=file_name, Body=final_response)


def data_chunk(paragraph, chunk_size=5000):
    # chunk the data due to comprehend limitation
    text_list = []
    while paragraph:
        text_list.append(str(paragraph[:chunk_size]))
        paragraph = paragraph[chunk_size:]
    return text_list


def average_sentiment(response):
    # averaging sentiment score
    positive, negative, neutral, mixed = 0, 0, 0, 0

    for score in response["ResultList"]:
        positive += score["SentimentScore"]["Positive"]
        negative += score["SentimentScore"]["Negative"]
        neutral += score["SentimentScore"]["Neutral"]
        mixed += score["SentimentScore"]["Mixed"]

    total_record = len(response["ResultList"])

    mapping = {
        "POSITIVE": positive / total_record,
        "NEGATIVE": negative / total_record,
        "NEUTRAL": neutral / total_record,
        "MIXED": mixed / total_record,
    }

    response = json.dumps(
        [
            {
                "Sentiment": max(mapping, key=mapping.get),
                "SentimentScore": {
                    "Positive": mapping["POSITIVE"],
                    "Negative": mapping["NEGATIVE"],
                    "Neutral": mapping["NEUTRAL"],
                    "Mixed": mapping["MIXED"],
                },
            }
        ]
    )
    return response
