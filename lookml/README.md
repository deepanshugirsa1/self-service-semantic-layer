# LookML BI Serving Layer

A governed **Looker (LookML)** semantic layer and dashboard on top of this repo's dbt mart
(`mart_kpi_daily`). It turns the certified dbt metrics into self-serve BI without letting
consumers redefine business logic in the BI tool.

```
lookml/
  manifest.lkml
  models/
    semantic_layer.model.lkml   # connection, explore, row-level access_filter, freshness-tied cache
  views/
    mart_kpi_daily.view.lkml     # certified MRR / ARR / ARPU / Subscribers with grain + edge-case notes
  dashboards/
    executive_kpis.dashboard.lookml  # KPI tiles + per-plan breakdowns, certified fields only
```

## Governance baked in
- **Certified measures only** — grain, aggregation, and edge cases live in LookML/dbt, not in ad-hoc Looker fields.
- **Row-level access** — `access_filter` on `mart_kpi_daily.plan` scopes queries to the viewer's `allowed_plan` user attribute.
- **Freshness-tied caching** — a `datagroup` invalidates cache from the mart build, so BI never serves stale metrics.
- **One definition** — ARR derives from the certified MRR measure; ARPU recomputes from totals (not an average of ratios) to avoid skew.

## Wiring
Connect this project to a Looker instance with a connection named `redshift_analytics` pointing at the
schema that holds `mart_kpi_daily` (DuckDB locally, Redshift in production), and set an `allowed_plan`
user attribute for row-level access. Validated for LookML structure; wire to a live Looker + warehouse
connection to render dashboards end to end.
