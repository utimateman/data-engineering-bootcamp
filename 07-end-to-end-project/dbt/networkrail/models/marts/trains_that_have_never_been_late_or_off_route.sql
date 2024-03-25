WITH train_that_never_late AS (
    SELECT
        train_id,
        MAX(CASE WHEN variation_status = 'LATE' THEN 1 ELSE 0 END) AS has_late_status
    FROM {{ ref('fct_movements') }}  
    GROUP BY train_id
)

SELECT train_id
FROM train_that_never_late
WHERE has_late_status = 0
