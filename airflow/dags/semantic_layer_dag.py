"""Airflow DAG stub — wire to production Airflow in Phase 2."""
from datetime import datetime

# from airflow import DAG
# from airflow.operators.bash import BashOperator
#
# with DAG("semantic_layer_daily", start_date=datetime(2026, 1, 1), schedule="@daily") as dag:
#     dbt_run = BashOperator(task_id="dbt_build", bash_command="dbt build --profiles-dir .")
