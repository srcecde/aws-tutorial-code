import sys
import json
import logging
import traceback
from botocore.exceptions import ClientError


def process_error():
    ex_type, ex_value, ex_traceback = sys.exc_info()
    traceback_string = traceback.format_exception(ex_type, ex_value, ex_traceback)
    error_msg = json.dumps(
        {
            "errorType": ex_type.__name__,
            "errorMessage": str(ex_value),
            "stackTrace": traceback_string,
        }
    )
    return error_msg


def check_file_exists(s3, BUCKET_NAME, FILE_PATH):
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=FILE_PATH)
        return True
    except ClientError:
        logging.error("File does not exists")
        return False


def create_presigned_url(s3_client, bucket_name, object_name, expiration=60):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response
