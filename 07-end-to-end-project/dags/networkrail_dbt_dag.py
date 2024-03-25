from airflow.utils import timezone

from cosmos import DbtDag, ProjectConfig, ProfileConfig
from cosmos.profiles import GoogleCloudServiceAccountDictProfileMapping

"""
#### Connections
1. **networkrail_dbt_bigquery_conn**
    [
        conn_type=`Google Cloud`,
        keyfile_json=`data-engineer-bootcamp-416105-b26ee1807d97.json`,
        project_id=`data-engineer-bootcamp-416105`
    ]
"""

profile_config = ProfileConfig(
    profile_name="networkrail",
    target_name="dev",
    profile_mapping=GoogleCloudServiceAccountDictProfileMapping(
        conn_id="networkrail_dbt_bigquery_conn",
        profile_args={
            "schema": "dbt_krai",
            "location": "asia-southeast1",
            "project_id":"data-engineer-bootcamp-416105"
        },
    ),
)

networkrail_dbt_dag = DbtDag(
    dag_id="networkrail_dbt_dag",
    schedule_interval="@hourly",
    start_date=timezone.datetime(2024, 3, 24),
    catchup=False,
    project_config=ProjectConfig("/opt/airflow/dbt/networkrail"),
    profile_config=profile_config,
    tags=["DEB", "2024", "networkrail", "dbt"],
)