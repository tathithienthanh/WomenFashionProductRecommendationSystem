USE eCommerce;

DELIMITER //
CREATE TRIGGER update_orderdetail_unitprice_before_insert
BEFORE INSERT ON orderdetail
FOR EACH ROW
BEGIN
    DECLARE product_price DOUBLE;
    DECLARE product_discount DOUBLE;
    
    SELECT price, IFNULL(discount, 0) INTO product_price, product_discount
    FROM Product
    WHERE product_id = NEW.product_id;
    
    SET NEW.unit_price = product_price * (1 - product_discount);
END//
DELIMITER;

DELIMITER //
CREATE TRIGGER update_orderdetail_unitprice_after_update
AFTER UPDATE ON Product
FOR EACH ROW
BEGIN
    IF NEW.price <> OLD.price OR IFNULL(NEW.discount, 0) <> IFNULL(OLD.discount, 0) THEN
        UPDATE OrderDetail od
        JOIN Orders o ON od.order_id = o.order_id
        SET od.unit_price = NEW.price * (1 - IFNULL(NEW.discount, 0))
        WHERE od.product_id = NEW.product_id
        AND o.order_status IN ('pending', 'confirmed'); 
    END IF;
END//
DELIMITER;

DELIMITER //
CREATE TRIGGER update_product_rating_after_insert
AFTER INSERT ON Review
FOR EACH ROW
BEGIN
    UPDATE Product p
    SET p.rating = (
        SELECT IFNULL(AVG(rating), 0)
        FROM Review
        WHERE product_id = NEW.product_id
    )
    WHERE p.product_id = NEW.product_id;
END//
DELIMITER;

DELIMITER //
CREATE TRIGGER update_product_rating_after_delete
AFTER DELETE ON Review
FOR EACH ROW
BEGIN
    UPDATE Product p
    SET p.rating = (
        SELECT IFNULL(AVG(rating), 0)
        FROM Review
        WHERE product_id = OLD.product_id
    )
    WHERE p.product_id = OLD.product_id;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER update_order_total_after_insert
AFTER INSERT ON OrderDetail
FOR EACH ROW
BEGIN
    UPDATE Orders o
    SET o.total_price = (
        SELECT SUM(unit_price * quantity * (1 - IFNULL(discount, 0)))
        FROM OrderDetail
        WHERE order_id = NEW.order_id
    )
    WHERE o.order_id = NEW.order_id;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER update_order_total_after_update
AFTER UPDATE ON OrderDetail
FOR EACH ROW
BEGIN
    UPDATE Orders o
    SET o.total_price = (
        SELECT SUM(unit_price * quantity * (1 - IFNULL(discount, 0)))
        FROM OrderDetail
        WHERE order_id = NEW.order_id
    )
    WHERE o.order_id = NEW.order_id;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER update_order_total_after_delete
AFTER DELETE ON OrderDetail
FOR EACH ROW
BEGIN
    UPDATE Orders o
    SET o.total_price = (
        SELECT IFNULL(SUM(unit_price * quantity * (1 - IFNULL(discount, 0))), 0)
        FROM OrderDetail
        WHERE order_id = OLD.order_id
    )
    WHERE o.order_id = OLD.order_id;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_product_quantity_before_insert
BEFORE INSERT ON OrderDetail
FOR EACH ROW
BEGIN
    DECLARE available_qty INT;
    
    SELECT quantity INTO available_qty 
    FROM Product WHERE product_id = NEW.product_id;
    
    IF available_qty < NEW.quantity THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Sản phẩm không đủ số lượng tồn kho';
    END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER update_product_quantity_after_update
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
	IF NEW.order_status = 'cancelled' AND OLD.order_status != 'cancelled' THEN
        UPDATE Product p
        JOIN OrderDetail od ON p.product_id = od.product_id
        SET 
            p.quantity = p.quantity + od.quantity,
            p.sold = p.sold - od.quantity
        WHERE od.order_id = NEW.order_id;
    END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER secure_admin_password_before_insert
BEFORE INSERT ON admin
FOR EACH ROW
BEGIN
    CALL validate_password(NEW.password);
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER secure_admin_password_before_update
BEFORE UPDATE ON admin
FOR EACH ROW
BEGIN
    IF NEW.password <> OLD.password THEN
        CALL validate_password(NEW.password);
    END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER secure_customer_password_before_insert
BEFORE INSERT ON customer
FOR EACH ROW
BEGIN
    CALL validate_password(NEW.password);
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER secure_customer_password_before_update
BEFORE UPDATE ON customer
FOR EACH ROW
BEGIN
    IF NEW.password <> OLD.password THEN
        CALL validate_password(NEW.password);
    END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER prevent_change_activitylog_before_insert
BEFORE INSERT ON ActivityLog
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'ActivityLog chỉ cho phép ghi từ hệ thống!';
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER prevent_change_activitylog_before_update
BEFORE INSERT ON ActivityLog
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'ActivityLog chỉ cho phép ghi từ hệ thống!';
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER prevent_change_activitylog_before_delete
BEFORE DELETE ON ActivityLog
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'ActivityLog chỉ cho phép ghi từ hệ thống!';
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_product_discount_before_insert
BEFORE INSERT ON Product
FOR EACH ROW
BEGIN
    IF NEW.discount IS NOT NULL THEN
        IF NEW.discount < 0 OR NEW.discount > 1 THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'Giá trị discount phải nằm trong khoảng từ 0 đến 1 (0% đến 100%)';
        END IF;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_product_discount_before_update
BEFORE UPDATE ON Product
FOR EACH ROW
BEGIN
    IF NEW.discount IS NOT NULL AND (NEW.discount <> OLD.discount) THEN
        IF NEW.discount < 0 OR NEW.discount > 1 THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'Giá trị discount phải nằm trong khoảng từ 0 đến 1 (0% đến 100%)';
        END IF;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_customer_email_before_insert
BEFORE INSERT ON Customer
FOR EACH ROW
BEGIN
    IF NEW.email NOT REGEXP '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,4}$' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Email khách hàng không hợp lệ';
    END IF;
    
    IF EXISTS (SELECT 1 FROM Customer WHERE email = NEW.email) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Email đã tồn tại trong hệ thống';
    END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_customer_email_before_update
BEFORE UPDATE ON Customer
FOR EACH ROW
BEGIN
    IF NEW.email NOT REGEXP '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,4}$' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Email khách hàng không hợp lệ';
    END IF;
    
    IF NEW.email <> OLD.email AND EXISTS (SELECT 1 FROM Customer WHERE email = NEW.email) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Email đã tồn tại trong hệ thống';
    END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_admin_email_before_insert
BEFORE INSERT ON admin
FOR EACH ROW
BEGIN
    IF NEW.email NOT REGEXP '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,4}$' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Email không hợp lệ';
    END IF;
    
    IF EXISTS (SELECT 1 FROM admin WHERE email = NEW.email) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Email đã tồn tại trong hệ thống';
    END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_admin_email_before_update
BEFORE UPDATE ON admin
FOR EACH ROW
BEGIN
    IF NEW.email NOT REGEXP '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,4}$' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Email không hợp lệ';
    END IF;
    
    IF NEW.email <> OLD.email AND EXISTS (SELECT 1 FROM admin WHERE email = NEW.email) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Email đã tồn tại trong hệ thống';
    END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_orders_shippeddate_before_insert
BEFORE INSERT ON Orders
FOR EACH ROW
BEGIN
    IF NEW.shipped_date IS NOT NULL THEN
        IF NEW.shipped_date < NEW.order_date THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Ngày giao hàng không thể trước ngày đặt hàng';
        END IF;
    END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_orders_shippeddate_before_update
BEFORE UPDATE ON Orders
FOR EACH ROW
BEGIN
    IF NEW.shipped_date IS NOT NULL AND NEW.shipped_date <> OLD.shipped_date THEN
        IF NEW.shipped_date < NEW.order_date THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Ngày giao hàng không thể trước ngày đặt hàng';
        END IF;
    END IF;
END//
DELIMITER ;