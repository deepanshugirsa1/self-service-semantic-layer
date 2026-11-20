# Connection: DuckDB locally, Redshift-ready (mirrors the repo's dbt profiles).
connection: "redshift_analytics"

include: "/lookml/views/*.view.lkml"
include: "/lookml/dashboards/*.dashboard.lookml"

# Cache tied to the dbt mart build so BI never serves stale certified metrics.
datagroup: semantic_layer_default_datagroup {
  sql_trigger: SELECT MAX(loaded_at) FROM mart_kpi_daily ;;
  max_cache_age: "1 hour"
}

persist_with: semantic_layer_default_datagroup

explore: kpi_daily {
  label: "Subscription KPIs (Certified)"
  description: "Governed explore over the dbt mart_kpi_daily. Measures carry explicit grain, aggregation, and edge-case handling; only certified fields are exposed."
  from: mart_kpi_daily

  # Row-level access: a viewer sees only the plan tier(s) in their Looker user attribute.
  access_filter: {
    field: mart_kpi_daily.plan
    user_attribute: allowed_plan
  }
}
