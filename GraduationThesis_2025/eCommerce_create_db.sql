CREATE DATABASE eCommerce;
USE eCommerce;

ALTER DATABASE eCommerce CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE OrderStatus (
	status_id VARCHAR(50) PRIMARY KEY,
    description VARCHAR(255)
);

CREATE TABLE Permission (
	permission_id VARCHAR(50) PRIMARY KEY,
    description VARCHAR(255)
);

CREATE TABLE Payment (
	payment_id VARCHAR(50) PRIMARY KEY,
    description VARCHAR(255)
);

CREATE TABLE Category (
	category_id VARCHAR(50) PRIMARY KEY,
    description VARCHAR(255)
);

CREATE TABLE Customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    last_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15),
    address VARCHAR(255)
);

CREATE TABLE Admin (
    admin_id VARCHAR(50) PRIMARY KEY,
    last_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Product (
    product_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    price DOUBLE NOT NULL,
    quantity INT NOT NULL,
    image_url VARCHAR(255),
    discount DOUBLE,
    sold INT NOT NULL,
    rating FLOAT
);

CREATE TABLE AdminHasPermissions (
	permission_id VARCHAR(50),
    admin_id VARCHAR(50),
    PRIMARY KEY (permission_id, admin_id),
    FOREIGN KEY (permission_id) REFERENCES Permission(permission_id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES Admin(admin_id) ON DELETE CASCADE
);

CREATE TABLE ProductHasCategories (
	category_id VARCHAR(50),
    product_id VARCHAR(50),
    PRIMARY KEY (category_id, product_id),
    FOREIGN KEY (category_id) REFERENCES Category(category_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE CASCADE
);

CREATE TABLE Cart (
    customer_id VARCHAR(50),
    product_id VARCHAR(50),
    quantity INT NOT NULL,
    PRIMARY KEY (customer_id, product_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE CASCADE
);

CREATE TABLE Review (
    customer_id VARCHAR(50),
    product_id VARCHAR(50),
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (customer_id, product_id, created_at),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE CASCADE
);

CREATE TABLE Orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    order_status VARCHAR(50),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipped_date TIMESTAMP,
    address VARCHAR(255),
    note VARCHAR(255),
    total_price DOUBLE,
    payment VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES Customer (customer_id) ON DELETE CASCADE,
    FOREIGN KEY (order_status) REFERENCES OrderStatus (status_id),
    FOREIGN KEY (payment) REFERENCES Payment (payment_id)
);

CREATE TABLE OrderDetail (
    order_id VARCHAR(50),
    product_id VARCHAR(50),
    quantity INT NOT NULL,
    unit_price DOUBLE NOT NULL,
    discount FLOAT,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE CASCADE
);

CREATE TABLE ActivityLog (
	admin_id VARCHAR(50),
    activity VARCHAR(255) NOT NULL,
    activity_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (admin_id, activity_time),
    FOREIGN KEY (admin_id) REFERENCES Admin(admin_id) ON DELETE CASCADE
);