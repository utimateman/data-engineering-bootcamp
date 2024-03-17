from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils import timezone

with DAG(
    dag_id="example_dag_1",
    start_date=timezone.datetime(2024, 3, 10), 
    schedule=None,
    tags=["DEB", "Skooldio"],
):
    t1 = EmptyOperator(task_id="t1") 
    t2 = EmptyOperator(task_id="t2") 

    t1 >> t2
