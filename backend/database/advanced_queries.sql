WITH ordered AS (
    SELECT id, quarter, revenue, expenses,
           revenue - expenses AS profit,
           ROUND(((revenue - expenses) / revenue) * 100, 2) AS margin,
           LAG(revenue) OVER (ORDER BY id) AS prev_revenue
    FROM financials
)
SELECT quarter,
       revenue,
       expenses,
       profit,
       margin,
       ROUND(((revenue - prev_revenue) / prev_revenue) * 100, 2) AS growth_rate
FROM ordered;
