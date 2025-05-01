USE eCommerce;

DELIMITER //
CREATE PROCEDURE GetRevenueReport (IN start_date DATE, IN end_date DATE)
BEGIN
	SELECT DATE(order_date) AS order_day, COUNT(*) AS total_orders, SUM(total_price) AS total_revenue, AVG(total_price) AS avg_order_value
    FROM Orders
    WHERE order_date BETWEEN start_date AND end_date
    AND order_status NOT IN ('cancelled', 'pending')
    GROUP BY DATE(order_date)
    ORDER BY order_day;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE UpdateInventory (IN p_product_id VARCHAR(50), IN quantity_change INT, IN is_increase BOOLEAN)
BEGIN
	DECLARE current_qty INT;
    
    IF is_increase THEN
        UPDATE Product 
        SET quantity = quantity + quantity_change
        WHERE product_id = p_product_id;
	ELSE
        SELECT quantity INTO current_qty 
        FROM Product 
        WHERE product_id = p_product_id;
        
        IF current_qty < quantity_change THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'Số lượng tồn kho không đủ';
        ELSE
            UPDATE Product 
            SET quantity = quantity - quantity_change
            WHERE product_id = p_product_id;
        END IF;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE ProcessOrder(IN p_order_id VARCHAR(50), IN new_status VARCHAR(50))
BEGIN
    DECLARE current_status VARCHAR(50);
    DECLARE order_exists INT;
    DECLARE is_valid_transition BOOLEAN DEFAULT FALSE;
    
    SELECT COUNT(*) INTO order_exists FROM Orders WHERE order_id = p_order_id;
    IF order_exists = 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Đơn hàng không tồn tại';
    END IF;
    
    SELECT order_status INTO current_status 
    FROM Orders 
    WHERE order_id = p_order_id;
    
    IF current_status = 'cancelled' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Không thể thay đổi trạng thái đơn hàng đã hủy';
    END IF;
    
    IF current_status = 'shipped' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Không thể thay đổi trạng thái đơn hàng đã hoàn thành';
    END IF;
    
    CASE 
        WHEN current_status = 'pending' AND new_status = 'confirmed' THEN
            SET is_valid_transition = TRUE;
            
        WHEN current_status = 'confirmed' AND new_status = 'processing' THEN
            SET is_valid_transition = TRUE;
            
        WHEN current_status = 'processing' AND new_status = 'shipped' THEN
            SET is_valid_transition = TRUE;
        ELSE
            SET is_valid_transition = FALSE;
    END CASE;
    
    IF NOT is_valid_transition THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Chuyển trạng thái không hợp lệ';
    END IF;
    IF new_status = 'shipped' THEN
		UPDATE Orders
        SET shipped_date = NOW()
        WHERE order_id = p_order_id;
	END IF;
    
    UPDATE Orders 
    SET order_status = new_status
    WHERE order_id = p_order_id;
    
    SELECT CONCAT('Đã cập nhật đơn hàng ', p_order_id, ' từ ', current_status, ' sang ', new_status) AS message;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE ValidatePassword (INOUT p_password VARCHAR(255))
BEGIN
	DECLARE is_valid BOOLEAN DEFAULT TRUE;
    DECLARE error_message VARCHAR(255) DEFAULT '';
    
    IF LENGTH(NEW.password) < 8 THEN
		SET is_valid = FALSE;
        SET error_message = CONCAT(error_message, 'Mật khẩu phải có ít nhất 8 ký tự. ');
    END IF;
    
    IF NEW.password NOT REGEXP '[0-9]' THEN
        SET is_valid = FALSE;
        SET error_message = CONCAT(error_message, 'Mật khẩu phải chứa ít nhất 1 số. ');
    END IF;
    
    IF NEW.password NOT REGEXP '[A-Za-z]' THEN
        SET is_valid = FALSE;
        SET error_message = CONCAT(error_message, 'Mật khẩu phải chứa ít nhất 1 chữ cái. ');
    END IF;
    
    IF NEW.password NOT REGEXP '[!@#$%^&*(),.?":{}|<>]' THEN
        SET is_valid = FALSE;
        SET error_message = CONCAT(error_message, 'Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt. ');
    END IF;
    
    IF NOT is_valid THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = error_message;
    END IF;
    
    SET p_password = SHA2(p_password, 256);
END//
DELIMITER ;

DELIMITER //
CREATE PROCEDURE ValidatePassword (INOUT p_password VARCHAR(255))
BEGIN
    DECLARE is_valid BOOLEAN DEFAULT TRUE;
    DECLARE error_message VARCHAR(255) DEFAULT '';

    IF LENGTH(p_password) < 8 THEN
        SET is_valid = FALSE;
        SET error_message = CONCAT(error_message, 'Mật khẩu phải có ít nhất 8 ký tự. ');
    END IF;

    IF p_password NOT REGEXP '[0-9]' THEN
        SET is_valid = FALSE;
        SET error_message = CONCAT(error_message, 'Mật khẩu phải chứa ít nhất 1 số. ');
    END IF;

    IF p_password NOT REGEXP '[A-Za-z]' THEN
        SET is_valid = FALSE;
        SET error_message = CONCAT(error_message, 'Mật khẩu phải chứa ít nhất 1 chữ cái. ');
    END IF;

    IF p_password NOT REGEXP '[!@#$%^&*(),.?":{}|<>]' THEN
        SET is_valid = FALSE;
        SET error_message = CONCAT(error_message, 'Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt. ');
    END IF;

    IF NOT is_valid THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = error_message;
    END IF;

    SET p_password = SHA2(p_password, 256);
END//
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetSalesReport (IN start_date DATE, IN end_date DATE, IN p_category_id VARCHAR(50))
BEGIN
    SELECT p.product_id, p.name, c.description AS category, SUM(od.quantity) AS total_sold, SUM(od.quantity * od.unit_price * (1 - IFNULL(od.discount, 0))) AS total_revenue
    FROM OrderDetail od JOIN Orders o ON od.order_id = o.order_id
		JOIN Product p ON od.product_id = p.product_id
		LEFT JOIN ProductHasCategories phc ON p.product_id = phc.product_id
		LEFT JOIN Category c ON phc.category_id = c.category_id
    WHERE o.order_date BETWEEN start_date AND end_date AND o.order_status = 'shipped' AND (p_category_id IS NULL OR phc.category_id = p_category_id)
    GROUP BY p.product_id
    ORDER BY total_revenue DESC;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE TableToCSV(IN p_table_name VARCHAR(255), IN p_file_path VARCHAR(255), IN p_delimiter VARCHAR(10))
BEGIN
    DECLARE v_table_exists INT DEFAULT 0;
    
    SELECT COUNT(*) INTO v_table_exists 
    FROM information_schema.tables 
    WHERE table_schema = DATABASE() AND table_name = p_table_name;
    
    IF v_table_exists = 0 THEN
		SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Bảng không tồn tại';
    END IF;
    
    SET @sql = CONCAT(
        "SELECT * FROM ", p_table_name,
        " INTO OUTFILE '", p_file_path,
        "' FIELDS TERMINATED BY '", p_delimiter, "'",
        " ENCLOSED BY '\"'",
        " LINES TERMINATED BY '\n'"
    );
    
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
    
    SELECT CONCAT('Đã backup bảng ', p_table_name, ' ra file: ', p_file_path) AS result;
END //
DELIMITER ;