"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""

import json
from urllib.parse import unquote_plus
import boto3

transcribe = boto3.client("transcribe")


def lambda_handler(event, context):
    if event:
        file_obj = event["Records"][0]
        bucket_name = str(file_obj["s3"]["bucket"]["name"])
        file_name = unquote_plus(str(file_obj["s3"]["object"]["key"]))
        s3_uri = create_uri(bucket_name, file_name)
        job_name = context.aws_request_id

        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": s3_uri},
            MediaFormat="mp3",
            LanguageCode="en-US",
            OutputBucketName="bucket-name",
            Settings={
                # 'VocabularyName': 'string',
                "ShowSpeakerLabels": True,
                "MaxSpeakerLabels": 2,
                "ChannelIdentification": False,
            },
        )

    return {"statusCode": 200, "body": json.dumps("Transcription job created!")}


def create_uri(bucket_name, file_name):
    return "s3://" + bucket_name + "/" + file_name
