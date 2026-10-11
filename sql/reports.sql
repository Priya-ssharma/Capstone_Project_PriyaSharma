
-- (i) ALTER + UPDATE with CASE.
-- Run the ALTER statement only once.

SET SQL_SAFE_UPDATES = 0;

ALTER TABLE customers
ADD COLUMN loyalty_tier VARCHAR(10);

UPDATE customers
SET loyalty_tier = CASE
    WHEN city_tier = 1 THEN 'Gold'
    ELSE 'Silver'
END;


-- (i) Check loyalty tier counts
-- Output:
-- Gold   | 28
-- Silver | 17

SELECT loyalty_tier, COUNT(*) AS customers
FROM customers
GROUP BY loyalty_tier;
