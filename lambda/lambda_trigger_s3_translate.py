# -*- coding: utf-8 -*-
__author__ = "Chirag Rathod (Srce Cde)"
__license__ = "MIT"
__email__ = "chiragr83@gmail.com"
__maintainer__ = "Chirag Rathod (Srce Cde)"

import json
from urllib.parse import unquote_plus
import boto3


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    translate = boto3.client("translate")
    if event:
        file_obj = event["Records"][0]
        bucket_name = str(file_obj["s3"]["bucket"]["name"])
        filename = unquote_plus(str(file_obj["s3"]["object"]["key"]))
        fileObj = s3.get_object(Bucket=bucket_name, Key=filename)
        file_content = fileObj["Body"].read().decode("utf-8")
        data = dataChunk(file_content)
        trans_data = []

        for d in data:
            response = translate.translate_text(
                Text=d, SourceLanguageCode="en", TargetLanguageCode="es"
            )
            trans_data.append(response["TranslatedText"])
        s3.put_object(
            Bucket=bucket_name,
            Key="{}_translate.txt".format(filename.split(".")[0]),
            Body=str(" ".join(trans_data)),
        )

    return {"statusCode": 200, "body": json.dumps("Thanks")}


def dataChunk(paragraph):
    text_list = []
    while paragraph:
        text_list.append(str(paragraph[:5000]))
        paragraph = paragraph[5000:]
    return text_list
