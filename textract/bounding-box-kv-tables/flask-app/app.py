import os
import time
from flask import Flask, render_template, request
from aws_requests_auth.aws_auth import AWSRequestsAuth
import requests
import uuid
import base64
import shutil
from config import Config

app = Flask(__name__)

config = Config()


@app.route("/", methods=["GET", "POST"])
def index():
    if "uploadFile" in request.files:
        try:
            shutil.rmtree("static/temp")
        except:
            pass
        os.makedirs("static/temp", exist_ok=True)
        uploaded_file = request.files.get("uploadFile", None)
        uploaded_file = uploaded_file.read()
        file_name = f"{uuid.uuid4().hex}.png"

        endpoint = f"{config.ENDPOINT}/upload?filename={file_name}"
        response = requests.get(endpoint, auth=sign())
        response = response.json()

        files = {"file": (file_name, uploaded_file)}
        http_response = requests.post(
            response["url"], data=response["fields"], files=files
        )
        full_filename = download_processed_file(file_name)

        with open(f"static/temp/{file_name}", "wb") as f:
            f.write(full_filename)
        processed_image = os.path.join("static/temp", file_name)
        uploaded_file = base64.b64encode(uploaded_file).decode("utf-8")
    else:
        processed_image = None
        uploaded_file = None

    return render_template(
        "home.html", processed_image=processed_image, uploaded_file=uploaded_file
    )


def sign():
    auth = AWSRequestsAuth(
        aws_access_key=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        aws_host=config.HOST,
        aws_region="us-east-1",
        aws_service="execute-api",
    )
    return auth


def download_processed_file(file_name):
    while True:
        endpoint = f"{config.ENDPOINT}/download?filename={file_name}"
        response = requests.get(endpoint, auth=sign())
        if response.status_code == 200:
            response = requests.get(response.text)
            return response.content
        time.sleep(1)
