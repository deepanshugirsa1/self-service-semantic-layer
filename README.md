# Self-Service Reporting & Semantic Layer Platform

Unified data model and governed semantic layer with **30+ metric definitions**, **data contracts**, dbt on Redshift (DuckDB locally), and Tableau-ready marts.

> **Status: ~60% complete.** dbt marts, 30+ metric YAML definitions, data contracts, and Airflow DAG stub run locally. Production Redshift + Tableau workbooks planned.

## Quickstart

```bash
pip install -r requirements.txt
python data/generate_data.py
dbt build --profiles-dir .
python run_demo.py
```

See [docs/ROADMAP.md](docs/ROADMAP.md).
