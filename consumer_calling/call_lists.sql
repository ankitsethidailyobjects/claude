-- Call lists for the Nov-26 brand & creative calling round.
-- Each block below becomes a row in the sheet's "Call List SQL" tab.
-- ASSUMED column names (check before running): v_order_customer_type(order_id, customer_id,
-- order_date, delivered_flag), v_lines_valid(order_id, product_name, category),
-- customers(customer_id, name, phone, city, dnd_flag). Swap in the real names if they differ.

-- @@ 0 · Shared base (prefix to each query)
WITH orders AS (
  SELECT o.customer_id, o.order_id, DATE(o.order_date) AS order_date,
         STRING_AGG(DISTINCT l.product_name, ', ') AS products,
         LOGICAL_OR(REGEXP_CONTAINS(LOWER(l.product_name), r'pedal backpack|commute messenger|canvas')) AS has_canvas
  FROM v_order_customer_type o
  JOIN v_lines_valid l USING (order_id)
  WHERE o.delivered_flag
  GROUP BY 1, 2, 3
),
cust AS (
  SELECT customer_id,
         COUNT(*) AS n_orders,
         MIN(order_date) AS first_order,
         MAX(order_date) AS last_order,
         ARRAY_AGG(products ORDER BY order_date DESC LIMIT 1)[OFFSET(0)] AS last_products,
         STRING_AGG(IF(has_canvas, products, NULL), ' | ') AS canvas_products,
         MAX(IF(has_canvas, order_date, NULL)) AS last_canvas_date,
         COUNTIF(has_canvas) AS n_canvas_orders
  FROM orders GROUP BY 1
)

-- @@ 1 · Main cohorts (First-time, O2, Power, Lapsed)
SELECT cohort, c.name AS customer_name, c.phone, c.city,
       k.last_order AS last_purchase_date, k.last_products, k.canvas_products, k.n_orders
FROM (
  SELECT *, CASE
      WHEN n_orders = 1 AND last_order >= DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY) THEN 'First-time (NTP)'
      WHEN n_orders = 2 AND last_order >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY) THEN 'Second-time (O2)'
      WHEN n_orders >= 3 AND last_order >= DATE_SUB(CURRENT_DATE(), INTERVAL 120 DAY) THEN 'Power / O3+'
      WHEN n_orders >= 2 AND last_order < DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH) THEN 'Lapsed'
    END AS cohort
  FROM cust) k
JOIN customers c USING (customer_id)
WHERE cohort IS NOT NULL AND c.phone IS NOT NULL AND NOT IFNULL(c.dnd_flag, FALSE)
QUALIFY ROW_NUMBER() OVER (PARTITION BY cohort ORDER BY FARM_FINGERPRINT(CAST(customer_id AS STRING))) <= 40
ORDER BY cohort, last_purchase_date DESC

-- @@ 2 · Canvas range buyers
-- Canvas order delivered 3 weeks–6 months ago; loyal (2+ orders or 2+ canvas orders) listed first.
SELECT 'Canvas range buyers' AS cohort, c.name AS customer_name, c.phone, c.city,
       k.last_order AS last_purchase_date, k.last_products, k.canvas_products, k.n_orders,
       k.last_canvas_date
FROM cust k
JOIN customers c USING (customer_id)
WHERE k.last_canvas_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
                             AND DATE_SUB(CURRENT_DATE(), INTERVAL 21 DAY)
  AND c.phone IS NOT NULL AND NOT IFNULL(c.dnd_flag, FALSE)
ORDER BY (k.n_orders >= 2 OR k.n_canvas_orders >= 2) DESC, k.last_canvas_date DESC
LIMIT 50

-- @@ 3 · ATC (not in warehouse orders)
-- Pull from MoEngage / GA4: added to cart in last 30 days, no order in that window.
-- Join phone numbers from customers on customer_id / email. Cap at 40.
