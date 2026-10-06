-- Part 1, Task 3: reports (MySQL).

USE priyadb6;

-- (a) Order totals

SELECT COUNT(*) AS total_orders,
       ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_revenue,
       ROUND(AVG(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS avg_order_value
FROM orders o
JOIN products p ON o.product_id = p.product_id;

-- (b) COUNT(*) vs COUNT(column)

SELECT COUNT(*) AS all_rows,
       COUNT(rating) AS rated_rows,
       COUNT(*) - COUNT(rating) AS unrated_rows
FROM orders;

-- (c1) LEFT JOIN: customers with zero orders

SELECT c.customer_id, c.name
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) = 0;

-- (c2) Independent check with NOT IN

SELECT customer_id, name
FROM customers
WHERE customer_id NOT IN (SELECT DISTINCT customer_id FROM orders);

-- (d) Return rate by city above 20%

SELECT c.city,
       COUNT(*) AS total_orders,
       SUM(o.returned) AS returned_orders,
       ROUND(100.0 * SUM(o.returned) / COUNT(*), 1) AS return_rate_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20
ORDER BY return_rate_pct DESC;

-- (e1) Top 5 customers by spend
-- Tie-break on customer_id: customers with equal spend would otherwise come back in arbitrary order, so LIMIT/OFFSET pages could overlap or skip rows.

SELECT c.customer_id, c.name,
       ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 5;

-- (e2) Ranks 3 to 5 via OFFSET
-- Same tie-break reason as (e1).

SELECT c.customer_id, c.name,
       ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 3 OFFSET 2;

-- (f) Revenue by category (three-table join)

SELECT p.category,
       COUNT(*) AS order_count,
       ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS category_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY p.category
ORDER BY category_revenue DESC;

-- (g) Names starting with A

SELECT * FROM customers WHERE name LIKE 'A%';

-- (h) Distinct acquisition sources

SELECT DISTINCT acquisition_source FROM customers;

-- (i) ALTER + UPDATE with CASE. Run the ALTER and UPDATE ONCE ONLY (the ALTER fails the second time).

SET SQL_SAFE_UPDATES = 0;
ALTER TABLE customers ADD COLUMN loyalty_tier VARCHAR(10);
UPDATE customers
SET loyalty_tier = CASE WHEN city_tier = 1 THEN 'Gold' ELSE 'Silver' END;

-- (i) check

SELECT loyalty_tier, COUNT(*) AS customers FROM customers GROUP BY loyalty_tier;


