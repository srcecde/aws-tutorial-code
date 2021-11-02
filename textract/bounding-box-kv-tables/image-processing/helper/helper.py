import sys
import json
import io
import traceback
import numpy as np
import cv2


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


def upload_to_s3(s3_client, bytes_buffer, BUCKET_NAME, key):
    s3_client.put_object(Body=bytes_buffer.getvalue(), Bucket=BUCKET_NAME, Key=key)


async def drawBoundingBox(image, height, width, box, color_code, thickness):
    left = int(width * box["Left"])
    top = int(height * box["Top"])
    cv2.rectangle(
        image,
        (left, top),
        (int(left + (width * box["Width"])), int(top + (height * box["Height"]))),
        color_code,
        thickness,
    )


def get_width_height(s3, bucketname, filename):
    file_obj = s3.get_object(Bucket=bucketname, Key=filename)
    file_content = file_obj["Body"].read()
    np_array = np.fromstring(file_content, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    height, width, _ = image.shape
    return image, height, width


async def process_response(response, s3, bucketname, filename):
    image, height, width = get_width_height(s3, bucketname, filename)

    for block in response["Blocks"]:
        if block["BlockType"] == "KEY_VALUE_SET":
            if block["EntityTypes"][0] == "KEY":
                await drawBoundingBox(
                    image,
                    height,
                    width,
                    block["Geometry"]["BoundingBox"],
                    (0, 0, 255),
                    1,
                )
            else:
                await drawBoundingBox(
                    image,
                    height,
                    width,
                    block["Geometry"]["BoundingBox"],
                    (0, 255, 0),
                    1,
                )

        if block["BlockType"] == "TABLE":
            await drawBoundingBox(
                image, height, width, block["Geometry"]["BoundingBox"], (255, 0, 0), 2
            )

        if block["BlockType"] == "CELL":
            await drawBoundingBox(
                image, height, width, block["Geometry"]["BoundingBox"], (0, 255, 255), 1
            )

        if block["BlockType"] == "SELECTION_ELEMENT":
            if block["SelectionStatus"] == "SELECTED":
                await drawBoundingBox(
                    image,
                    height,
                    width,
                    block["Geometry"]["BoundingBox"],
                    (0, 0, 255),
                    1,
                )

    _, en_buffer = cv2.imencode(".png", image)
    byte_im = en_buffer.tobytes()
    io_buf = io.BytesIO(byte_im)
    upload_to_s3(s3, io_buf, bucketname, f'processed/{filename.split("/")[-1]}')

    return True
