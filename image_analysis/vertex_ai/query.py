import base64
import os
import shutil
import sys
import tempfile

import requests

from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from sys import argv

import credentials


def query_endpoint(imagePath):
    endpoint = credentials.endpoint
    with open(imagePath, "rb") as f:
        file_content = f.read()

    encoded_content = base64.b64encode(file_content).decode("utf-8")
    instance = predict.instance.ImageClassificationPredictionInstance(
        content=encoded_content,
    ).to_value()
    instances = [instance]
    prediction = endpoint.predict(instances)
    print(prediction)


if len(argv) == 3:
    if argv[1] == "1":
        if os.path.exists(argv[2]):
            print("Querying endpoint...")
            query_endpoint(argv[2])
        else:
            raise FileNotFoundError
    if argv[1] == "2":
        image_url = argv[2]
        filename = image_url.split("/")[-1]
        r = requests.get(image_url, stream=True)

        if r.status_code == 200:
            r.raw.decode_content = True

            with tempfile.NamedTemporaryFile() as temp:
                shutil.copyfileobj(r.raw, temp)
                print("Downloaded image")
                print("Querying endpoint...")
                query_endpoint(temp.name)
        else:
            print("Could not download image")
            sys.exit()

else:
    print("Please input two arguments.")
