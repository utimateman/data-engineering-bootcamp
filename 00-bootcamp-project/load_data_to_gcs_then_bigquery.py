import json
import os

from google.cloud import bigquery, storage
from google.oauth2 import service_account


DATA_FOLDER = "data"
BUSINESS_DOMAIN = "greenery"
location = "asia-southeast1"

# Prepare and Load Credentials to Connect to GCP Services
keyfile_gcs = "data-engineer-bootcamp-416105-7b0ce102eddf.json"
service_account_info_gcs = json.load(open(keyfile_gcs))
credentials_gcs = service_account.Credentials.from_service_account_info(
    service_account_info_gcs
)

keyfile_bigquery = "data-engineer-bootcamp-416105-378e0ec03e71.json"
service_account_info_bigquery = json.load(open(keyfile_bigquery))
credentials_bigquery = service_account.Credentials.from_service_account_info(
    service_account_info_bigquery
)

project_id = "data-engineer-bootcamp-416105"

# Load data from Local to GCS
bucket_name = "deb-bootcamp-99"
storage_client = storage.Client(
    project=project_id,
    credentials=credentials_gcs,
)
bucket = storage_client.bucket(bucket_name)

data_list = ["addresses","events","order_items","orders","products","promos","users"]
data = "addresses"

file_path = f"{DATA_FOLDER}/{data}.csv"
destination_blob_name = f"{BUSINESS_DOMAIN}/{data}/{data}.csv"

# ---------- PARTITION --------------------------------

# PARTITION #1
data = "events"
dt = "2021-02-10"
partition = dt.replace("-", "")
file_path = f"{DATA_FOLDER}/{data}.csv"
destination_blob_name = f"{BUSINESS_DOMAIN}/{data}/{dt}/{data}.csv"

# YOUR CODE HERE TO LOAD DATA TO GCS
# ส่วนอัพโหลดไฟล์จาก Local ขึ้นไปยัง GCS
blob = bucket.blob(destination_blob_name)
blob.upload_from_filename(file_path)

# Load data from GCS to BigQuery
bigquery_client = bigquery.Client(
    project=project_id,
    credentials=credentials_bigquery,
    location=location,
)
# PARTITION #2
table_id = f"{project_id}.deb_bootcamp.{data}${partition}"

# # NON PARTITION
# table_id = f"{project_id}.deb_bootcamp.{data}"

job_config = bigquery.LoadJobConfig(
    skip_leading_rows=1,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    source_format=bigquery.SourceFormat.CSV,
    autodetect=True,
    time_partitioning=bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="created_at",) # partition #3
)
job = bigquery_client.load_table_from_uri(
    f"gs://{bucket_name}/{destination_blob_name}",
    table_id,
    job_config=job_config,
    location=location,
)
job.result()

table = bigquery_client.get_table(table_id)
print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}")


# ---------- NON-PARTITION --------------------------------


# PARTITION #1
data = "addresses"
file_path = f"{DATA_FOLDER}/{data}.csv"
destination_blob_name = f"{BUSINESS_DOMAIN}/{data}/{data}.csv"

# YOUR CODE HERE TO LOAD DATA TO GCS
# ส่วนอัพโหลดไฟล์จาก Local ขึ้นไปยัง GCS
blob = bucket.blob(destination_blob_name)
blob.upload_from_filename(file_path)

# Load data from GCS to BigQuery
bigquery_client = bigquery.Client(
    project=project_id,
    credentials=credentials_bigquery,
    location=location,
)
# PARTITION #2
#table_id = f"{project_id}.deb_bootcamp.{data}${partition}"

# NON PARTITION
table_id = f"{project_id}.deb_bootcamp.{data}"

job_config = bigquery.LoadJobConfig(
    skip_leading_rows=1,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    source_format=bigquery.SourceFormat.CSV,
    autodetect=True,
)
job = bigquery_client.load_table_from_uri(
    f"gs://{bucket_name}/{destination_blob_name}",
    table_id,
    job_config=job_config,
    location=location,
)
job.result()

table = bigquery_client.get_table(table_id)
print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}")

