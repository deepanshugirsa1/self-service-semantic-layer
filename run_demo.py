"""End-to-end demo: generate -> build marts -> contracts -> observability report."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.tasks import build_marts, build_observability_report, generate_data


def main() -> None:
    print("[1/3] Generating subscription data + load manifest...")
    generate_data()

    print("[2/3] Building KPI marts (DuckDB)...")
    marts = build_marts()
    print(f"      {marts['rows']} plan rows | total MRR ${marts['total_mrr']:,.2f}")

    print("[3/3] Publishing observability report (freshness + quality)...")
    report = build_observability_report()
    f = report["freshness"]
    q = report["quality"]
    print(f"      overall={report['overall_status']} | freshness {f['age_hours']}h/"
          f"{f['sla_hours']}h {f['status']} | quality {q['pass_rate'] * 100:.0f}% "
          f"({q['passed']}/{q['passed'] + q['failed']} checks)")
    print(f"      metrics registered={report['semantic_layer']['metrics_registered']}")
    print("\nArtifacts: artifacts/observability_report.json, artifacts/observability.html")
    print("Dashboard: streamlit run observability/dashboard.py")


if __name__ == "__main__":
    main()
