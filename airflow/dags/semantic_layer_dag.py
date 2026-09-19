"""Airflow DAG for the self-serve semantic layer.

Daily pipeline: generate -> build marts -> enforce contracts -> publish
observability report (freshness + quality). Retries and a freshness SLA make
reliability enforceable, not aspirational.

The `airflow` import is guarded so the module also imports cleanly in CI /
local environments without a scheduler installed; the task callables live in
`pipeline.tasks` and are unit-testable on their own.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.tasks import (  # noqa: E402
    build_marts,
    build_observability_report,
    enforce_contracts,
    generate_data,
)

DEFAULT_ARGS = {
    "owner": "data-platform",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "sla": timedelta(hours=6),
}

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator

    with DAG(
        dag_id="semantic_layer_daily",
        description="Foundational semantic-layer build with freshness + quality gates",
        start_date=datetime(2026, 1, 1),
        schedule="@daily",
        catchup=False,
        default_args=DEFAULT_ARGS,
        tags=["semantic-layer", "data-quality", "observability"],
    ) as dag:
        t_generate = PythonOperator(task_id="generate_data", python_callable=generate_data)
        t_marts = PythonOperator(task_id="build_marts", python_callable=build_marts)
        t_contracts = PythonOperator(task_id="enforce_contracts", python_callable=enforce_contracts)
        t_observability = PythonOperator(
            task_id="publish_observability", python_callable=build_observability_report
        )

        t_generate >> t_marts >> t_contracts >> t_observability
except ImportError:  # airflow not installed (CI / local) — tasks still importable
    dag = None
