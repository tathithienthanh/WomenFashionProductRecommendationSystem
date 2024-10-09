-- Tạo cơ sở dữ liệu
CREATE DATABASE RCM_System;
GO

-- Sử dụng cơ sở dữ liệu vừa tạo
USE RCM_System;
GO

-- Tạo bảng Customers
CREATE TABLE Customers (
    ID INT PRIMARY KEY,               -- Khóa chính
    Name NVARCHAR(255) NOT NULL       -- Tên khách hàng
);
GO

-- Tạo bảng Products
CREATE TABLE Products (
    ID INT PRIMARY KEY,               -- Khóa chính
    Name NVARCHAR(255) NOT NULL,      -- Tên sản phẩm
    Price DECIMAL(10, 2) NOT NULL,    -- Giá sản phẩm
    Sold INT NOT NULL,                -- Số lượng đã bán
    Category NVARCHAR(255) NOT NULL,  -- Danh mục sản phẩm
    Quantity INT NOT NULL             -- Số lượng tồn kho
);
GO

-- Tạo bảng Feedbacks
CREATE TABLE Feedbacks (
    ID_Product INT,                           -- Khóa ngoại từ Products
    ID_Customer INT,                          -- Khóa ngoại từ Customers
    Content NVARCHAR(MAX) NOT NULL,           -- Nội dung phản hồi
    SentScore INT NOT NULL,                   -- Điểm cảm xúc
    SentLabel NVARCHAR(50) NOT NULL,          -- Nhãn cảm xúc (tiêu cực, trung tính, tích cực)
    PRIMARY KEY (ID_Product, ID_Customer),    -- Khóa chính
    FOREIGN KEY (ID_Product) REFERENCES Products(ID),   -- Thiết lập khóa ngoại tới bảng Products
    FOREIGN KEY (ID_Customer) REFERENCES Customers(ID)  -- Thiết lập khóa ngoại tới bảng Customers
);
GO

-- Tạo bảng HistoryOfTransactions
CREATE TABLE HistoryOfTransactions (
    ID_Customer INT,                          -- Khóa ngoại từ Customers
    ID_Product INT,                           -- Khóa ngoại từ Products
    Time DATETIME NOT NULL,                   -- Thời gian giao dịch
    Quantity INT NOT NULL,                    -- Số lượng mua
    PRIMARY KEY (ID_Customer, ID_Product, Time),  -- Khóa chính bao gồm ID_Customer, ID_Product và Time
    FOREIGN KEY (ID_Customer) REFERENCES Customers(ID),   -- Khóa ngoại tới bảng Customers
    FOREIGN KEY (ID_Product) REFERENCES Products(ID)      -- Khóa ngoại tới bảng Products
);
GO

-- Tạo bảng HistoryOfSearches
CREATE TABLE HistoryOfSearches (
    ID_Customer INT,                          -- Khóa ngoại từ Customers
    Time DATETIME NOT NULL,                   -- Thời gian tìm kiếm
    Content NVARCHAR(MAX) NOT NULL,           -- Nội dung tìm kiếm
    Category NVARCHAR(255),                   -- Danh mục tìm kiếm
    PRIMARY KEY (ID_Customer, Time),          -- Khóa chính
    FOREIGN KEY (ID_Customer) REFERENCES Customers(ID)   -- Khóa ngoại tới bảng Customers
);
GO
