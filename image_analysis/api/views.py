from curses.ascii import isalnum
import string

from django.shortcuts import render
import base64
import shutil
import sys
import tempfile
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from google.oauth2 import service_account
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from collections import OrderedDict
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from api import models as appname_models
from api.models import Image
from django.db import connection
import csv
import json
import sys
import os.path
import os
import sys
from pathlib import Path
from time import sleep
from gcloud import storage
from google.oauth2 import service_account
import os
import httplib2
import vertex_ai.credentials
from os.path import exists


@api_view(["GET"])
def endpoint_view(request, image_url):
    ans = query_endpoint(image_url)
    names = ans.predictions[0].get("displayNames")
    confidences = ans.predictions[0].get("confidences")
    dictionary = OrderedDict(zip(names, confidences))
    final_ans = sorted(dictionary.items(), key=lambda x: x[1], reverse=True)

    if len(final_ans) > 5:
        final_ans = final_ans[:6]

    return Response(final_ans)


def query_endpoint(image_url):
    filename = image_url.split("/")[-1]
    r = requests.get(image_url, stream=True)

    if r.status_code == 200:
        r.raw.decode_content = True

        with tempfile.NamedTemporaryFile() as temp:
            shutil.copyfileobj(r.raw, temp)
            print("Downloaded image")
            print("Querying endpoint...")
            endpoint = vertex_ai.credentials.endpoint
            with open(temp.name, "rb") as f:
                file_content = f.read()

            encoded_content = base64.b64encode(file_content).decode("utf-8")
            instance = predict.instance.ImageClassificationPredictionInstance(
                content=encoded_content,
            ).to_value()
            instances = [instance]
            prediction = endpoint.predict(instances)
            return prediction

    else:
        print("Could not download image")
        sys.exit()


@api_view(["POST"])
def upload(request):
    studentDict = json.loads(request.body)
    queryset = Image.objects.all().delete()
    f = open("image_holder/image_classification_multi_label.csv", "w")

    directory = os.path.realpath(os.path.dirname(__file__)) + "/../image_holder"
    if not exists(directory):
        os.mkdir(directory)

    path = os.path.join(sys.path[0], "image_holder")
    print(path)

    stop = 0
    item_size = 0
    hit_array = studentDict["hits"]["hits"]
    list_str = get_top_labels(hit_array)
    for item in studentDict["hits"]["hits"]:
        if (
            len(item["_source"]["additionalImageUrls"])
        ) <= 75:  # != 2 when testing for tommrow < 75
            continue
        stop = 1 + stop
        bucket = 0

        item["_source"]["additionalImageUrls"].append(item["_source"]["imageUrl"])
        n = ""
        for stri in item["_source"]["name"].split():
            for i in stri:
                if isalnum(i):
                    n = n + i
        for l in item["_source"]["additionalImageUrls"]:
            lab_str = str(item["_source"]["category"]) + "," + "  " + n
            labelsStr = ""
            print(n)
            for ext in list_str:
                if "and" in ext or "of" in ext:
                    continue
                if ext in lab_str:
                    print(ext)
                    labelsStr = "," + ext + labelsStr
            k = (
                vertex_ai.credentials.staging_bucket
                + "/"
                + str(n)
                + str(bucket)
                + ".jpg"
                + ","
                + n
                + labelsStr
            )
            f.write(k + "\n")

            img_data = requests.get(l).content

            with open(path + "/" + n + str(bucket) + ".jpg", "wb") as handler:
                handler.write(img_data)
            bucket = bucket + 1

        # k.save()
        if stop == 2:
            break

    # printcsv("Train")
    print(item_size)

    # print( connection.queries[1])
    return Response("done")


@api_view(["POST"])
def post_data(view):
    path = os.path.join(Path(sys.path[0]).parent, "image_analysis/image_holder")
    filelist = os.listdir(path)
    storage_client = storage.Client(project=vertex_ai.credentials.project)
    bucket = storage_client.get_bucket(vertex_ai.credentials.staging_bucket_name)

    for name in filelist:
        blob = bucket.blob(name)
        print(name)
        blob.upload_from_filename(path + "/" + name)
    print("done")
    return Response("done")


@api_view(["PUT"])
def create_data_set(head):
    l = [vertex_ai.credentials.staging_bucket + "/image_classification_multi_label.csv"]
    print(l)
    import_dataset(
        vertex_ai.credentials.project,
        vertex_ai.credentials.location,
        l,
        "gs://google-cloud-aiplatform/schema/dataset/ioformat/image_classification_multi_label_io_format_1.0.0.yaml",
        vertex_ai.credentials.dataset_id,
    )
    return Response("done")


@api_view(["POST"])
def create_model(request, model_name):
    myDataset = aiplatform.ImageDataset(vertex_ai.credentials.dataset_id)
    job = aiplatform.AutoMLImageTrainingJob(
        display_name=model_name + "_JOB",
        model_type="CLOUD",
        multi_label=True,
    )
    model = job.run(
        dataset=myDataset,
        training_fraction_split=0.6,
        validation_fraction_split=0.2,
        test_fraction_split=0.2,
        budget_milli_node_hours=8000,
        model_display_name=model_name,
        disable_early_stopping=False,
    )
    model.deploy(
        traffic_percentage=100,
        endpoint=vertex_ai.credentials.endpoint,
        deployed_model_display_name="Deployed_" + model_name,
        min_replica_count=1,
        max_replica_count=1,
        sync=True,
    )
    if vertex_ai.credentials.model != None:
        print("Deleting Model" + counter)
        vertex_ai.credentials.model.delete()
        vertex_ai.credentials.model.wait()
    vertex_ai.credentials.model = model
    print("___End of algorithm")
    return Response("done")


def import_dataset(
    project: str,
    location: str,
    src_uris: list,
    import_schema_uri: str,
    dataset_id: str,
):
    ds = aiplatform.ImageDataset(dataset_id)
    ds = ds.import_data(
        gcs_source=src_uris, import_schema_uri=import_schema_uri, sync=True
    )

    print(ds.display_name)
    print(ds.name)
    print(ds.resource_name)
    return ds


def get_top_labels(hits_array) -> list:
    to_return = {}
    i = 0
    for item in hits_array:
        if len(item["_source"]["additionalImageUrls"]) >= 75:
            name = item["_source"]["name"]
            i = i + 1
            if i == 4:
                break
            category = item["_source"]["category"]
            words = category.split(" ") + name.split(" ")

            for word in words:
                word = word.strip("()")
                word = word.strip(string.digits)

                if str(word).isalnum():
                    if word in to_return.keys():
                        to_return[word] = (
                            to_return[word]
                            + len(item["_source"]["additionalImageUrls"])
                            + 1
                        )
                    else:
                        to_return[word] = (
                            len(item["_source"]["additionalImageUrls"]) + 1
                        )
            print(to_return)
    to_return = dict(sorted(to_return.items(), key=lambda it: it[1]))

    lowest_20_percent = list(to_return.keys())[
        0 : int(len(list(to_return.keys())) * 0.2)
    ]

    to_return = dict(sorted(to_return.items(), key=lambda it: it[1], reverse=True))

    [to_return.pop(key) for key in lowest_20_percent]

    return list(to_return.keys())
