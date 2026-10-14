
-- Part 1, Task 3: Reports (MySQL)

USE priyadb6;


-- Order totals
-- Expected output: 180 orders, revenue 99860.20, average order value 554.78

SELECT COUNT(*) AS total_orders,
       ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_revenue,
       ROUND(AVG(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS avg_order_value
FROM orders o
JOIN products p ON o.product_id = p.product_id;


-- COUNT(*) vs COUNT(column)
-- Expected output: 180 rows, 165 rated rows, 15 unrated rows

SELECT COUNT(*) AS all_rows,
       COUNT(rating) AS rated_rows,
       COUNT(*) - COUNT(rating) AS unrated_rows
FROM orders;


-- Customers with zero orders using LEFT JOIN
-- Expected output: C045 | Vihaan

SELECT c.customer_id, c.name
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) = 0;


-- Customers with zero orders using NOT IN
-- Expected output: C045 | Vihaan

SELECT customer_id, name
FROM customers
WHERE customer_id NOT IN (
    SELECT DISTINCT customer_id
    FROM orders
);


-- Return rate by city above 20%
-- Expected output:
-- Jaipur    | 19 orders | 8 returned | 42.1%
-- Lucknow   | 49 orders | 15 returned | 30.6%
-- Bangalore | 33 orders | 8 returned | 24.2%

SELECT c.city,
       COUNT(*) AS total_orders,
       SUM(o.returned) AS returned_orders,
       ROUND(100.0 * SUM(o.returned) / COUNT(*), 1) AS return_rate_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20
ORDER BY return_rate_pct DESC;


-- Top 5 customers by spend
-- Expected output:
-- C043 | Reyansh | 12920.00
-- C026 | Isha    | 8371.60
-- C008 | Meera   | 4564.60
-- C011 | Arjun   | 4111.00
-- C042 | Sanya   | 3785.00

SELECT c.customer_id,
       c.name,
       ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 5;


-- Customer spending ranks 3 to 5 using OFFSET
-- Expected output:
-- C008 | Meera | 4564.60
-- C011 | Arjun | 4111.00
-- C042 | Sanya | 3785.00

SELECT c.customer_id,
       c.name,
       ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 3 OFFSET 2;


-- Revenue by category
-- Expected output:
-- Haircare     | 54 orders | 44956.10
-- Skincare     | 60 orders | 27346.00
-- Babycare     | 30 orders | 16805.00
-- PersonalCare | 36 orders | 10753.10

SELECT p.category,
       COUNT(*) AS order_count,
       ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS category_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY category_revenue DESC;


-- Customer names starting with A
-- Expected output: 10 rows
-- C001 | Aarav
-- C003 | Aditi
-- C004 | Ananya
-- C011 | Arjun
-- C021 | Aryan
-- C030 | Anika
-- C031 | Aditya
-- C036 | Aisha
-- C041 | Ayaan
-- C044 | Aria

SELECT *
FROM customers
WHERE name LIKE 'A%';


-- Distinct acquisition sources
-- Expected output: 4 sources
-- Organic
-- Referral
-- Ad
-- Social

SELECT DISTINCT acquisition_source
FROM customers;


-- Add and update loyalty tier
-- Run ALTER TABLE only if loyalty_tier does not already exist.

SET SQL_SAFE_UPDATES = 0;

ALTER TABLE customers
ADD COLUMN loyalty_tier VARCHAR(10);

UPDATE customers
SET loyalty_tier = CASE
    WHEN city_tier = 1 THEN 'Gold'
    ELSE 'Silver'
END;


-- Count customers by loyalty tier
-- Expected output:
-- Gold   | 28
-- Silver | 17

SELECT loyalty_tier,
       COUNT(*) AS customers
FROM customers
GROUP BY loyalty_tier
ORDER BY loyalty_tier;
