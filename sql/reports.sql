
-- Part 1, Task 3: Reports (MySQL)

USE priyadb6;


-- 1. Order totals
-- Output:
-- total_orders | total_revenue | avg_order_value
-- 180          | 99860.20      | 554.78

SELECT
    COUNT(*) AS total_orders,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_revenue,
    ROUND(AVG(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS avg_order_value
FROM orders o
JOIN products p ON o.product_id = p.product_id;


-- 2. COUNT(*) vs COUNT(column)
-- Output:
-- all_rows | rated_rows | unrated_rows
-- 180      | 165        | 15

SELECT
    COUNT(*) AS all_rows,
    COUNT(rating) AS rated_rows,
    COUNT(*) - COUNT(rating) AS unrated_rows
FROM orders;


-- 3. Customers with zero orders using LEFT JOIN
-- Output:
-- customer_id | name
-- C045        | Vihaan

SELECT c.customer_id, c.name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) = 0;


-- 4. Customers with zero orders using NOT IN
-- Output:
-- customer_id | name
-- C045        | Vihaan

SELECT customer_id, name
FROM customers
WHERE customer_id NOT IN (
    SELECT DISTINCT customer_id
    FROM orders
    WHERE customer_id IS NOT NULL
);


-- 5. Return rate by city above 20%
-- Output:
-- city      | total_orders | returned_orders | return_rate_pct
-- Jaipur    | 19           | 8               | 42.1
-- Lucknow   | 49           | 15              | 30.6
-- Bangalore | 33           | 8               | 24.2

SELECT
    c.city,
    COUNT(o.order_id) AS total_orders,
    SUM(o.returned) AS returned_orders,
    ROUND(100.0 * SUM(o.returned) / COUNT(o.order_id), 1) AS return_rate_pct
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20
ORDER BY return_rate_pct DESC;


-- 6. Top 5 customers by spend
-- Tie-break: customer_id ASC ensures consistent ordering when spending ties.
-- Output:
-- customer_id | name    | total_spend
-- C043        | Reyansh | 12920.00
-- C026        | Isha    | 8371.60
-- C008        | Meera   | 4564.60
-- C011        | Arjun   | 4111.00
-- C042        | Sanya   | 3785.00

SELECT
    c.customer_id,
    c.name,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 5;


-- 7. Customer spending ranks 3 to 5 using OFFSET
-- Tie-break: customer_id ASC ensures consistent ordering when spending ties.
-- Output:
-- customer_id | name  | total_spend
-- C008        | Meera | 4564.60
-- C011        | Arjun | 4111.00
-- C042        | Sanya | 3785.00

SELECT
    c.customer_id,
    c.name,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 3 OFFSET 2;


-- 8. Revenue by category
-- Output:
-- category     | order_count | category_revenue
-- Haircare     | 54          | 44956.10
-- Skincare     | 60          | 27346.00
-- Babycare     | 30          | 16805.00
-- PersonalCare | 36          | 10753.10

SELECT
    p.category,
    COUNT(o.order_id) AS order_count,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS category_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY p.category
ORDER BY category_revenue DESC;


-- 9. Customer names starting with A
-- Output:
-- customer_id | name
-- C001        | Aarav
-- C003        | Aditi
-- C004        | Ananya
-- C011        | Arjun
-- C021        | Aryan
-- C030        | Anika
-- C031        | Aditya
-- C036        | Aisha
-- C041        | Ayaan
-- C044        | Aria

SELECT customer_id, name
FROM customers
WHERE name LIKE 'A%'
ORDER BY customer_id;


-- 10. Distinct acquisition sources
-- Output:
-- acquisition_source
-- Ad
-- Organic
-- Referral
-- Social

SELECT DISTINCT acquisition_source
FROM customers
ORDER BY acquisition_source;


-- 11. Add and update loyalty tier
-- Run ALTER TABLE only once.
-- If loyalty_tier already exists, skip the ALTER TABLE statement.

SET SQL_SAFE_UPDATES = 0;

ALTER TABLE customers
ADD COLUMN loyalty_tier VARCHAR(10);

UPDATE customers
SET loyalty_tier = CASE
    WHEN city_tier = 1 THEN 'Gold'
    ELSE 'Silver'
END;

SET SQL_SAFE_UPDATES = 1;


-- 12. Count customers by loyalty tier
-- Output:
-- loyalty_tier | customers
-- Gold         | 28
-- Silver       | 17

SELECT
    loyalty_tier,
    COUNT(*) AS customers
FROM customers
GROUP BY loyalty_tier
ORDER BY loyalty_tier;
