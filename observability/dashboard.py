"""Streamlit observability panel for the semantic layer.

Run:  streamlit run observability/dashboard.py
Reads artifacts/observability_report.json (produced by the pipeline).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "artifacts" / "observability_report.json"

st.set_page_config(page_title="Semantic Layer Observability", layout="wide")
st.title("Semantic Layer — Observability")

if not REPORT.exists():
    st.warning("No report yet. Run `python run_demo.py` first.")
    st.stop()

report = json.loads(REPORT.read_text(encoding="utf-8"))
fresh = report["freshness"]
q = report["quality"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Overall", report["overall_status"])
c2.metric("Freshness (h)", f"{fresh['age_hours']}", f"SLA {fresh['sla_hours']}h · {fresh['status']}")
c3.metric("Quality pass rate", f"{q['pass_rate'] * 100:.0f}%")
c4.metric("Metrics registered", report["semantic_layer"]["metrics_registered"])

st.subheader("Data-quality & contract checks")
st.dataframe(pd.DataFrame(q["checks"]), use_container_width=True)

st.caption(f"Dataset: {report['dataset']['name']} · rows {report['dataset']['rows']} · "
           f"generated {report['generated_at']}")
