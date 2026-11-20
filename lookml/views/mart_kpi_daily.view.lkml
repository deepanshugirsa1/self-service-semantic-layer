# Source: dbt mart `mart_kpi_daily` (plan, subscriber_count, total_mrr, arpu).
# Grain: one row per subscription plan. Certified measures aggregate across plans at query grain.
view: mart_kpi_daily {
  sql_table_name: mart_kpi_daily ;;

  dimension: plan {
    primary_key: yes
    type: string
    description: "Subscription plan tier. Governs row-level access via the allowed_plan user attribute."
    sql: ${TABLE}.plan ;;
  }

  # ---------- Certified measures (governed metric definitions) ----------

  measure: subscribers {
    label: "Subscribers"
    description: "Total subscribers. Grain: summed across plans. Edge case: inactive/test plans excluded upstream in dbt."
    type: sum
    sql: ${TABLE}.subscriber_count ;;
    value_format_name: decimal_0
  }

  measure: total_mrr {
    label: "MRR"
    description: "Monthly recurring revenue = SUM(total_mrr). Nulls coalesced to 0; negative MRR rejected by a dbt not-negative test."
    type: sum
    sql: COALESCE(${TABLE}.total_mrr, 0) ;;
    value_format_name: usd_0
  }

  measure: arr {
    label: "ARR"
    description: "Annual recurring revenue = MRR x 12. Derived from the certified MRR measure, not stored, to keep one definition."
    type: number
    sql: ${total_mrr} * 12 ;;
    value_format_name: usd_0
  }

  measure: arpu {
    label: "ARPU"
    description: "Average revenue per user = MRR / Subscribers at query grain. Deliberately recomputed from totals, not an average of per-plan ARPU, to avoid Simpson's-paradox skew."
    type: number
    sql: 1.0 * ${total_mrr} / NULLIF(${subscribers}, 0) ;;
    value_format_name: usd
  }
}
