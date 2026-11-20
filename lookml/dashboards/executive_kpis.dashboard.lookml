- dashboard: executive_kpis
  title: "Executive KPI Overview"
  layout: newspaper
  description: "Self-serve BI over the governed semantic layer. Every tile uses certified measures from mart_kpi_daily only."
  preferred_viewer: dashboards-next

  filters:
  - name: plan
    title: "Plan"
    type: field_filter
    default_value: ""
    allow_multiple_values: true
    model: semantic_layer
    explore: kpi_daily
    field: mart_kpi_daily.plan

  elements:
  - title: "MRR"
    name: mrr_kpi
    model: semantic_layer
    explore: kpi_daily
    type: single_value
    fields: [mart_kpi_daily.total_mrr]
    listen:
      plan: mart_kpi_daily.plan
    row: 0
    col: 0
    width: 6
    height: 3

  - title: "ARR"
    name: arr_kpi
    model: semantic_layer
    explore: kpi_daily
    type: single_value
    fields: [mart_kpi_daily.arr]
    listen:
      plan: mart_kpi_daily.plan
    row: 0
    col: 6
    width: 6
    height: 3

  - title: "ARPU by Plan"
    name: arpu_by_plan
    model: semantic_layer
    explore: kpi_daily
    type: looker_column
    fields: [mart_kpi_daily.plan, mart_kpi_daily.arpu]
    sorts: [mart_kpi_daily.arpu desc]
    listen:
      plan: mart_kpi_daily.plan
    row: 3
    col: 0
    width: 12
    height: 7

  - title: "Subscribers by Plan"
    name: subscribers_by_plan
    model: semantic_layer
    explore: kpi_daily
    type: looker_bar
    fields: [mart_kpi_daily.plan, mart_kpi_daily.subscribers]
    sorts: [mart_kpi_daily.subscribers desc]
    listen:
      plan: mart_kpi_daily.plan
    row: 10
    col: 0
    width: 12
    height: 7
