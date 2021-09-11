# -*- coding: utf-8 -*-
__author__ = "Chirag Rathod (Srce Cde)"
__license__ = "MIT"
__email__ = "chiragr83@gmail.com"
__maintainer__ = "Chirag Rathod (Srce Cde)"

import json
import cv2
import math
import boto3
import os
import uuid


def lambda_handler(event, context):
    s3_resource = boto3.resource("s3")
    s3_client = boto3.client("s3")
    try:
        file_obj = event["Records"][0]
        # extract bucket name from event data on trigger
        bucket_name = str(file_obj["s3"]["bucket"]["name"])
        # extract file name from event data on trigger
        file_name = str(file_obj["s3"]["object"]["key"])
        print(f"Bucket Name: {bucket_name}\nFileName: {file_name}")

        # temporary path to save video file
        tmp_file_path = "/tmp/{}".format(file_name)
        print(f"Temporary Path: {tmp_file_path}")

        # downloading file to the tmp path
        s3_resource.meta.client.download_file(bucket_name, file_name, tmp_file_path)

        # loading video source
        cap = cv2.VideoCapture(tmp_file_path)
        # initializing frame count
        frameCount = 0
        # deriving framerate
        frameRate = math.floor(cap.get(cv2.CAP_PROP_FPS))

        while cap.isOpened():
            # extracting frame
            ret, frame = cap.read()
            frameCount += 1
            if ret != True:
                break
            # capturing frame every 10 seconds
            if frameCount % (10 * frameRate) == 0:
                # basically converting numpy array to bytes
                res, im_jpg = cv2.imencode(".jpg", frame)
                # saving frame to s3
                s3_client.put_object(
                    Bucket="bucket-name",
                    Key="{}.jpg".format(uuid.uuid4()),
                    Body=im_jpg.tobytes(),
                )

    except Exception as e:
        print("Unable to extract frames : {}".format(e))
        return "Unable to extract frames"
