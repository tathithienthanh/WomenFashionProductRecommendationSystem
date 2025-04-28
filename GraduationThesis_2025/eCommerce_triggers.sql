USE eCommerce;

CREATE TRIGGER update_orderdetail_unitprice
BEFORE INSERT ON orderdetail
FOR EACH ROW
BEGIN
	DECLARE product_price DOUBLE;
    DECLARE prodcut_discount DOUBLE;
    
    SELECT price, ifnull(discount, 0) INTO product_price, product_discount
    FROM Product
    WHERE product_id = new.product_id;
    
    SET NEW.unit_price = product_price * (1 - product_discount);
END