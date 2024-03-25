WITH hour_with_highest_late AS (
    SELECT
        DATE_TRUNC(actual_timestamp_utc, HOUR) AS hour_period,
        COUNT(*) AS late_count
    FROM  {{ ref('fct_movements') }}
    WHERE variation_status = 'LATE'
    GROUP BY hour_period
    ORDER BY late_count DESC
)

SELECT
    hour_period,
    late_count
FROM hour_with_highest_late