from google.oauth2 import service_account
from google.cloud import aiplatform
import os

secretFile = (
    os.path.realpath(os.path.dirname(__file__))
    + "/../authentication/focus-cache-363618-870ccf96951d.json"
)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = secretFile

if not os.path.exists(secretFile):
    raise FileNotFoundError("The authentication file is not in the current directory.")
print("here")
myCredentials = service_account.Credentials.from_service_account_file(secretFile)
project = "focus-cache-363618"
location = "us-central1"
staging_bucket = "gs://image_bucket_labelings"
staging_bucket_name = "image_bucket_labelings"
dataset_id = "5908038814877614080"
model = None
endpoint = aiplatform.Endpoint("3985395399153156096")

aiplatform.init(
    project=project,
    location=location,
    staging_bucket=staging_bucket,
    credentials=myCredentials,
)
