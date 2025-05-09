USE eCommerce;

CREATE VIEW CustomerInfo AS
	SELECT customer_id, first_name, last_name, email, phone_number, address
	FROM Customer;

CREATE VIEW AdminInfo AS
	SELECT a.admin_id, a.first_name, a.last_name, a.email, COUNT(al.activity) AS total_activities, MAX(al.activity_time) AS last_activity_time
	FROM Admin a
	LEFT JOIN ActivityLog al ON a.admin_id = al.admin_id
	GROUP BY a.admin_id, a.first_name, a.last_name, a.email;

CREATE VIEW AdminActivityDetail AS
	SELECT a.admin_id, CONCAT(a.first_name, ' ', a.last_name) AS admin_name, al.activity, al.activity_time
	FROM Admin a
	JOIN ActivityLog al ON a.admin_id = al.admin_id
	ORDER BY al.activity_time DESC;

CREATE VIEW CustomerOrderHistory AS
	SELECT c.customer_id, CONCAT(c.first_name, ' ', c.last_name) AS customer_name, o.order_id, o.order_date, o.order_status, o.total_price, COUNT(od.product_id) AS total_items, GROUP_CONCAT(p.name SEPARATOR ', ') AS products
	FROM Customer c
	JOIN Orders o ON c.customer_id = o.customer_id
	JOIN OrderDetail od ON o.order_id = od.order_id
	JOIN Product p ON od.product_id = p.product_id
	WHERE o.order_status IN ('pending', 'confirm', 'processing', 'shipped', 'cancelled')
	GROUP BY o.order_id, c.customer_id, c.first_name, c.last_name, o.order_date, o.order_status, o.total_price;
    
CREATE VIEW LowInventory AS
	SELECT * FROM Product 
	WHERE quantity < 10
    ORDER BY p.quantity;
    
CREATE VIEW TopSellingProducts AS
	SELECT p.product_id, p.name AS product_name, p.price, p.discount, p.quantity AS stock, p.sold AS total_sold, ROUND(p.price * (1 - IFNULL(p.discount, 0)), 2) AS discounted_price, 
		SUM(od.quantity * od.unit_price * (1 - IFNULL(od.discount, 0))) AS total_revenue, ROUND(AVG(r.rating), 1) AS avg_rating
	FROM Product p
	LEFT JOIN OrderDetail od ON p.product_id = od.product_id
	LEFT JOIN Orders o ON od.order_id = o.order_id AND o.order_status = 'shipped'
	LEFT JOIN Review r ON p.product_id = r.product_id
	GROUP BY p.product_id
	ORDER BY total_sold DESC, total_revenue DESC
	LIMIT 50;
    
CREATE VIEW ProductReviewsSummary AS
    SELECT p.product_id, p.name AS product_name, COUNT(*) AS total_reviews, ROUND(AVG(r.rating), 1) AS avg_rating, 
		SUM(CASE WHEN r.rating = 5 THEN 1 ELSE 0 END) AS five_star,
        SUM(CASE WHEN r.rating = 4 THEN 1 ELSE 0 END) AS four_star,
        SUM(CASE WHEN r.rating = 3 THEN 1 ELSE 0 END) AS three_star,
        SUM(CASE WHEN r.rating = 2 THEN 1 ELSE 0 END) AS two_star,
        SUM(CASE WHEN r.rating = 1 THEN 1 ELSE 0 END) AS one_star,
        MAX(r.created_at) AS last_review_date
    FROM Product p
    LEFT JOIN Review r ON p.product_id = r.product_id
    GROUP BY p.product_id, p.name
    ORDER BY avg_rating DESC, total_reviews DESC;