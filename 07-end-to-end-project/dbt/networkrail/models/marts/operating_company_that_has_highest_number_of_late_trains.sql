WITH company_that_late AS (
    SELECT company_name, count(*) as late_cnt 
    FROM {{ ref('fct_movements') }}  
    WHERE variation_status = "LATE" 
    GROUP BY company_name 
    ORDER BY late_cnt DESC
)

SELECT * 
FROM company_that_late