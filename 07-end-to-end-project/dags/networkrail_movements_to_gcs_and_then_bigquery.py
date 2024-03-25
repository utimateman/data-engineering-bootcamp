import csv
import json
import logging


import psycopg2





from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils import timezone

from google.cloud import bigquery, storage
from google.oauth2 import service_account


DAGS_FOLDER = "/opt/airflow/dags"
BUSINESS_DOMAIN = "networkrail"
DATA = "movements"
LOCATION = "asia-southeast1"
PROJECT_ID = "data-engineer-bootcamp-416105"
GCS_BUCKET = "deb4-bootcamp-99"
BIGQUERY_DATASET = "networkrail"
KEYFILE_FOR_GCS = "/opt/airflow/dags/data-engineer-bootcamp-416105-7b0ce102eddf.json"
KEYFILE_FOR_GCS_TO_BIGQUERY = "/opt/airflow/dags/data-engineer-bootcamp-416105-b26ee1807d97.json"


def _extract_data(**context):
    ds = context["data_interval_start"].to_date_string()

    pg_hook = PostgresHook(
        postgres_conn_id="networkrail_postgres_conn",
        schema="networkrail",
        schedule="@hourly",
        tags=["DEB", "Skooldio"],
        catchup=False,
    )
    connection = pg_hook.get_conn()
    cursor = connection.cursor()

    # Your code here
    table = "movements"
    header = [
        "event_type",
        "gbtt_timestamp",
        "original_loc_stanox",
        "planned_timestamp",
        "timetable_variation",
        "original_loc_timestamp",
        "current_train_id",
        "delay_monitoring_point",
        "next_report_run_time",
        "reporting_stanox",
        "actual_timestamp",
        "correction_ind",
        "event_source",
        "train_file_address",
        "platform",
        "division_code",
        "train_terminated",
        "train_id",
        "offroute_ind",
        "variation_status",
        "train_service_code",
        "toc_id",
        "loc_stanox",
        "auto_expected",
        "direction_ind",
        "route",
        "planned_event_type",
        "next_report_stanox",
        "line_ind",
    ]
    # ลองดึงข้อมูลจากตาราง order_items และเขียนลงไฟล์ CSV
    with open(f"{DAGS_FOLDER}/movements-{ds}.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        query = f"select * from {table} where DATE(actual_timestamp) = '{ds}'"
        cursor.execute(query)

        results = cursor.fetchall()
        for each in results:
            writer.writerow(each)

    if results:
        return "load_data_to_gcs"
    else:
        return "do_nothing"


def _load_data_to_gcs(**context):
    ds = context["data_interval_start"].to_date_string()


    service_account_info_gcs = json.load(open(KEYFILE_FOR_GCS))
    credentials_gcs = service_account.Credentials.from_service_account_info(
        service_account_info_gcs
    )

    # Load data from Local to GCS
    bucket_name = "deb4-bootcamp-99"
    storage_client = storage.Client(
        project=PROJECT_ID,
        credentials=credentials_gcs,
    )
    bucket = storage_client.bucket(bucket_name)

    file_path = f"{DAGS_FOLDER}/{DATA}-{ds}.csv"
    destination_blob_name = f"{BUSINESS_DOMAIN}/{DATA}/{ds}/{DATA}.csv"
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(file_path)

    # Your code here


def _load_data_from_gcs_to_bigquery(**context):
    ds = context["data_interval_start"].to_date_string()

    service_account_info_bigquery = json.load(open(KEYFILE_FOR_GCS_TO_BIGQUERY))
    credentials_bigquery = service_account.Credentials.from_service_account_info(
        service_account_info_bigquery
    )

    bigquery_client = bigquery.Client(
        project=PROJECT_ID,
        credentials=credentials_bigquery,
        location=LOCATION,
    )
    bigquery_schema = [
        bigquery.SchemaField("event_type", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("gbtt_timestamp", bigquery.SqlTypeNames.TIMESTAMP),
        bigquery.SchemaField("original_loc_stanox", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("planned_timestamp", bigquery.SqlTypeNames.TIMESTAMP),
        bigquery.SchemaField("timetable_variation", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("original_loc_timestamp", bigquery.SqlTypeNames.TIMESTAMP),
        bigquery.SchemaField("current_train_id", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("delay_monitoring_point", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("next_report_run_time", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("reporting_stanox", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("actual_timestamp", bigquery.SqlTypeNames.TIMESTAMP),
        bigquery.SchemaField("correction_ind", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("event_source", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("train_file_address", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("platform", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("division_code", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("train_terminated", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("train_id", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("offroute_ind", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("variation_status", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("train_service_code", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("toc_id", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("loc_stanox", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("auto_expected", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("direction_ind", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("route", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("planned_event_type", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("next_report_stanox", bigquery.SqlTypeNames.STRING),
        bigquery.SchemaField("line_ind", bigquery.SqlTypeNames.STRING),
    ]

    partition = ds.replace("-","")
    table_id = f"{PROJECT_ID}.networkrail.{DATA}${partition}"
    bigquery_schema = [
        bigquery.SchemaField("event_type", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("gbtt_timestamp", bigquery.enums.SqlTypeNames.TIMESTAMP),
        bigquery.SchemaField("original_loc_stanox", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("planned_timestamp", bigquery.enums.SqlTypeNames.TIMESTAMP),
        bigquery.SchemaField("timetable_variation", bigquery.enums.SqlTypeNames.INTEGER),
        bigquery.SchemaField("original_loc_timestamp", bigquery.enums.SqlTypeNames.TIMESTAMP),
        bigquery.SchemaField("current_train_id", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("delay_monitoring_point", bigquery.enums.SqlTypeNames.BOOLEAN),
        bigquery.SchemaField("next_report_run_time", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("reporting_stanox", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("actual_timestamp", bigquery.enums.SqlTypeNames.TIMESTAMP),
        bigquery.SchemaField("correction_ind", bigquery.enums.SqlTypeNames.BOOLEAN),
        bigquery.SchemaField("event_source", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("train_file_address", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("platform", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("division_code", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("train_terminated", bigquery.enums.SqlTypeNames.BOOLEAN),
        bigquery.SchemaField("train_id", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("offroute_ind", bigquery.enums.SqlTypeNames.BOOLEAN),
        bigquery.SchemaField("variation_status", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("train_service_code", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("toc_id", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("loc_stanox", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("auto_expected", bigquery.enums.SqlTypeNames.BOOLEAN),
        bigquery.SchemaField("direction_ind", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("route", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("planned_event_type", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("next_report_stanox", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("line_ind", bigquery.enums.SqlTypeNames.STRING),
    ]
    job_config = bigquery.LoadJobConfig(
        skip_leading_rows=1,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        source_format=bigquery.SourceFormat.CSV,
        schema=bigquery_schema,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="actual_timestamp",
        ),
    )

    bucket_name = "deb4-bootcamp-99"
    destination_blob_name = f"{BUSINESS_DOMAIN}/{DATA}/{ds}/{DATA}.csv"
    job = bigquery_client.load_table_from_uri(
        f"gs://{bucket_name}/{destination_blob_name}",
        table_id,
        job_config=job_config,
        location=LOCATION,
    )
    job.result()

    table = bigquery_client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}")

    # Your code here


default_args = {
    "owner": "Skooldio",
    "start_date": timezone.datetime(2024, 3, 24),
}
with DAG(
    dag_id="networkrail_movements_to_gcs_and_then_bigquery",
    default_args=default_args,
    schedule=None,  # Set the schedule here
    catchup=False,
    tags=["DEB", "2024", "networkrail"],
    max_active_runs=3,
):

    # Start
    start = EmptyOperator(task_id="start")

    # Extract data from NetworkRail Postgres Database
    # extract_data = EmptyOperator(task_id="extract_data")
    extract_data = BranchPythonOperator(
        task_id="extract_data",
        python_callable=_extract_data,
    )

    # Do nothing
    do_nothing = EmptyOperator(task_id="do_nothing")

    # Load data to GCS
    # load_data_to_gcs = EmptyOperator(task_id="load_data_to_gcs")
    load_data_to_gcs = PythonOperator(
        task_id="load_data_to_gcs",
        python_callable=_load_data_to_gcs,
    )

    # Load data from GCS to BigQuery
    # load_data_from_gcs_to_bigquery = EmptyOperator(task_id="load_data_from_gcs_to_bigquery")
    load_data_from_gcs_to_bigquery = PythonOperator(
        task_id="load_data_from_gcs_to_bigquery",
        python_callable=_load_data_from_gcs_to_bigquery,
    )

    # End
    end = EmptyOperator(task_id="end", trigger_rule="one_success")

    # Task dependencies
    start >> extract_data >> load_data_to_gcs >> load_data_from_gcs_to_bigquery >> end
    extract_data >> do_nothing >> end