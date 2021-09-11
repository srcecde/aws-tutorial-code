"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""

import json
import boto3


def lambda_handler(event, context):
    if event:
        s3 = boto3.client("s3")
        s3_object = event["Records"][0]["s3"]
        bucket_name = s3_object["bucket"]["name"]
        file_name = s3_object["object"]["key"]
        file_obj = s3.get_object(Bucket=bucket_name, Key=file_name)
        transcript_result = json.loads(file_obj["Body"].read())

        segments = transcript_result["results"]["speaker_labels"]
        items = transcript_result["results"]["items"]

        speaker_text = []
        flag = False
        speaker_json = {}
        for no_of_speaker in range(segments["speakers"]):
            for word in items:
                for seg in segments["segments"]:
                    if seg["speaker_label"] == "spk_" + str(no_of_speaker):
                        end_time = seg["end_time"]
                        if "start_time" in word:
                            if seg["items"]:
                                for seg_item in seg["items"]:
                                    if (
                                        word["end_time"] == seg_item["end_time"]
                                        and word["start_time"] == seg_item["start_time"]
                                    ):
                                        speaker_text.append(
                                            word["alternatives"][0]["content"]
                                        )
                                        flag = True
                        elif word["type"] == "punctuation":
                            if flag and speaker_text:
                                temp = speaker_text[-1]
                                temp += word["alternatives"][0]["content"]
                                speaker_text[-1] = temp
                                flag = False
                                break

            speaker_json["spk_" + str(no_of_speaker)] = " ".join(speaker_text)
            speaker_text = []
    print(speaker_json)
    s3.put_object(Bucket="bucket-name", Key=file_name, Body=json.dumps(speaker_json))

    return {
        "statusCode": 200,
        "body": json.dumps("Speaker transcript seperated successfully!"),
    }
