# Self-Service Reporting & Semantic Layer Platform

Unified data model and governed **semantic layer** with **30+ metric definitions**, **data contracts**, dbt marts (DuckDB locally, Redshift-ready), an **Airflow** DAG, and a **freshness + data-quality observability** report.

> **Status: Complete (local portfolio).** Foundational entities are modeled once and reused: generate → DuckDB/dbt marts → contract + quality gates → freshness SLA → published observability report and Streamlit panel. Airflow DAG orchestrates the daily build with retries and a freshness SLA. Production Redshift wiring is documented as future scope.

## Pipeline

```
subscriptions (raw + load manifest)
        │
        ▼
  DuckDB / dbt marts  ──►  mart_kpi_daily (plan × MRR × ARPU × ARR)
        │
        ▼
  contract + quality gates   (schema, required, mrr >= 0, not-null)
        │
        ▼
  freshness SLA check        (age_hours vs contract freshness_sla_hours)
        │
        ▼
  observability report       artifacts/observability_report.json + .html
                             (+ Streamlit panel: observability/dashboard.py)
```

Orchestrated by `airflow/dags/semantic_layer_dag.py`:
`generate_data → build_marts → enforce_contracts → publish_observability`
with `retries=2` and a `6h` freshness SLA.

## Quickstart

```bash
pip install -r requirements.txt
python run_demo.py                        # full pipeline + observability report
streamlit run observability/dashboard.py  # live observability panel
```

Latest local run: **32 metrics registered**, freshness **PASS** (0.0h / 6h SLA), quality **100%** (8/8 checks), overall **HEALTHY**.

## What's included

| Component | Status |
|-----------|--------|
| 30+ governed metric definitions (`semantic_layer/metrics.yaml`) | Done |
| Data contract (schema, required fields, quality rules, freshness SLA) | Done |
| DuckDB / dbt KPI marts | Done |
| Contract + quality-gate enforcement | Done |
| Freshness SLA check (load manifest) | Done |
| Observability report (JSON + HTML) + Streamlit panel | Done |
| Airflow DAG (retries + freshness SLA) | Done |

## Stack

Python, SQL, dbt (dbt-duckdb), DuckDB (Redshift stand-in), Airflow, data contracts (YAML), Streamlit observability panel, pandas.

See [docs/ROADMAP.md](docs/ROADMAP.md) for production Redshift + BI wiring.
