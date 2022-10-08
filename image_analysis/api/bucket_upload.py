import os
import sys
from pathlib import Path
from time import sleep
from gcloud import storage
from google.oauth2 import service_account
import os
import credentials
import httplib2

path = os.path.join(Path(sys.path[0]).parent, "image_holder/")
filelist = os.listdir(path)
storage_client = storage.Client(project=credentials.project)
bucket = storage_client.get_bucket("image_labels_bucket")

for name in filelist:
    blob = bucket.blob(name)
    print(name)
    sleep(1)
    blob.upload_from_filename(path + name)
print("done")
