"""Pipeline tasks for the self-serve semantic layer.

Each function is an idempotent step the Airflow DAG calls via PythonOperator,
and that run_demo.py runs locally. Steps:

    generate_data -> build_marts -> enforce_contracts -> build_observability_report

Freshness, contract, and quality signals are computed and published so
reliability is *shown* (an observability report), not just claimed.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "subscriptions.csv"
MANIFEST = ROOT / "data" / "raw" / "_manifest.json"
CONTRACT = ROOT / "contracts" / "subscriptions_contract.yaml"
METRICS = ROOT / "semantic_layer" / "metrics.yaml"
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------------------------
def generate_data() -> None:
    from data.generate_data import main as gen

    gen()


# ----------------------------------------------------------------------------
def build_marts() -> dict:
    """Build the KPI mart with DuckDB (same grain as the dbt mart)."""
    import duckdb

    con = duckdb.connect()
    con.execute(f"CREATE VIEW subs AS SELECT * FROM read_csv_auto('{RAW.as_posix()}')")
    mart = con.execute(
        """
        SELECT plan,
               COUNT(*)        AS subscriber_count,
               ROUND(SUM(mrr),2)  AS total_mrr,
               ROUND(AVG(mrr),2)  AS arpu,
               ROUND(SUM(mrr)*12,2) AS total_arr
        FROM subs
        GROUP BY plan
        ORDER BY total_mrr DESC
        """
    ).df()
    con.close()
    mart.to_parquet(ARTIFACTS / "mart_kpi_daily.parquet", index=False)
    mart.to_csv(ARTIFACTS / "mart_kpi_daily.csv", index=False)
    return {"rows": int(mart.shape[0]), "total_mrr": float(mart["total_mrr"].sum())}


# ----------------------------------------------------------------------------
def _load_contract() -> dict:
    return yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))


def enforce_contracts() -> dict:
    """Validate schema, required columns, and quality rules from the contract."""
    contract = _load_contract()
    df = pd.read_csv(RAW)
    checks = []

    # schema / required columns
    for col in contract.get("schema", []):
        present = col["name"] in df.columns
        checks.append({"check": f"column_present:{col['name']}", "passed": bool(present)})
        if present and col.get("required"):
            nulls = int(df[col["name"]].isna().sum())
            checks.append({"check": f"not_null:{col['name']}", "passed": nulls == 0,
                           "violations": nulls})

    # declared quality rules
    rule_map = {
        "mrr >= 0": lambda d: int((d["mrr"] < 0).sum()),
        "user_id is not null": lambda d: int(d["user_id"].isna().sum()),
    }
    for rule in contract.get("quality_rules", []):
        violations = rule_map.get(rule, lambda d: 0)(df)
        checks.append({"check": f"rule:{rule}", "passed": violations == 0, "violations": violations})

    passed = sum(1 for c in checks if c["passed"])
    result = {
        "total_checks": len(checks),
        "passed": passed,
        "failed": len(checks) - passed,
        "pass_rate": round(passed / len(checks), 4) if checks else 1.0,
        "checks": checks,
    }
    (ARTIFACTS / "contract_checks.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


# ----------------------------------------------------------------------------
def compute_freshness() -> dict:
    """Hours since last load vs the contract freshness SLA."""
    contract = _load_contract()
    sla_hours = float(contract.get("freshness_sla_hours", 24))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    loaded_at = datetime.fromisoformat(manifest["loaded_at"])
    age_hours = (datetime.now(timezone.utc) - loaded_at).total_seconds() / 3600
    return {
        "loaded_at": manifest["loaded_at"],
        "age_hours": round(age_hours, 3),
        "sla_hours": sla_hours,
        "status": "PASS" if age_hours <= sla_hours else "FAIL",
    }


# ----------------------------------------------------------------------------
def build_observability_report() -> dict:
    """Combine freshness + contract + quality + registry into one report + HTML panel."""
    df = pd.read_csv(RAW)
    metrics = yaml.safe_load(METRICS.read_text(encoding="utf-8"))
    freshness = compute_freshness()
    contracts = enforce_contracts()

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "name": "subscriptions",
            "rows": int(df.shape[0]),
            "columns": list(df.columns),
        },
        "freshness": freshness,
        "quality": {
            "pass_rate": contracts["pass_rate"],
            "passed": contracts["passed"],
            "failed": contracts["failed"],
            "checks": contracts["checks"],
        },
        "semantic_layer": {"metrics_registered": len(metrics.get("metrics", []))},
        "overall_status": "HEALTHY" if freshness["status"] == "PASS" and contracts["failed"] == 0 else "DEGRADED",
    }
    (ARTIFACTS / "observability_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    _write_html(report)
    return report


def _write_html(report: dict) -> None:
    def badge(ok: bool) -> str:
        color = "#1a7f37" if ok else "#cf222e"
        text = "PASS" if ok else "FAIL"
        return f'<span style="color:#fff;background:{color};padding:2px 8px;border-radius:4px;">{text}</span>'

    fresh = report["freshness"]
    q = report["quality"]
    rows = "".join(
        f"<tr><td>{c['check']}</td><td>{badge(c['passed'])}</td>"
        f"<td>{c.get('violations', 0)}</td></tr>"
        for c in q["checks"]
    )
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Semantic Layer Observability</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;margin:24px;color:#111}}
h1{{font-size:20px}} table{{border-collapse:collapse;width:100%;margin-top:8px}}
td,th{{border:1px solid #ddd;padding:6px 10px;text-align:left;font-size:13px}}
.kpi{{display:inline-block;margin-right:24px}}</style></head><body>
<h1>Semantic Layer &mdash; Observability Report</h1>
<p>Generated {report['generated_at']} &middot; Overall: <b>{report['overall_status']}</b></p>
<div class="kpi">Rows: <b>{report['dataset']['rows']}</b></div>
<div class="kpi">Metrics registered: <b>{report['semantic_layer']['metrics_registered']}</b></div>
<div class="kpi">Freshness: <b>{fresh['age_hours']}h</b> / SLA {fresh['sla_hours']}h {badge(fresh['status']=='PASS')}</div>
<div class="kpi">Quality pass rate: <b>{q['pass_rate']*100:.0f}%</b></div>
<h2>Data-quality &amp; contract checks</h2>
<table><tr><th>Check</th><th>Status</th><th>Violations</th></tr>{rows}</table>
</body></html>"""
    (ARTIFACTS / "observability.html").write_text(html, encoding="utf-8")


def run_all() -> dict:
    generate_data()
    marts = build_marts()
    report = build_observability_report()
    return {"marts": marts, "observability": report}
