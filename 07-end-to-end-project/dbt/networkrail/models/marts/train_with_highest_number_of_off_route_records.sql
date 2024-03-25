-- train_with_highest_number_of_off_route_records.sql


WITH off_route_counts AS (
    SELECT
        train_id,
        COUNT(*) AS offroute_cnt
    FROM {{ ref('fct_movements') }}
    WHERE offroute_ind = true
    group by train_id
    ORDER BY offroute_cnt DESC
)

SELECT
    *
FROM off_route_counts
