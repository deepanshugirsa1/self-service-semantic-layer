SELECT
    plan,
    COUNT(*) AS subscriber_count,
    SUM(mrr) AS total_mrr,
    AVG(mrr) AS arpu
FROM {{ ref('stg_subscriptions') }}
GROUP BY plan
