-- Create database
CREATE DATABASE RCM_System;
GO

-- Use the newly created database
USE RCM_System;
GO

-- Create Customers table
CREATE TABLE Customers (
    ID INT PRIMARY KEY,               -- Primary key
    Name NVARCHAR(255) NOT NULL       -- Customer name
);
GO

-- Create Products table
CREATE TABLE Products (
    ID INT PRIMARY KEY,               -- Primary key
    Name NVARCHAR(255) NOT NULL,      -- Product name
    Price DECIMAL(10, 2) NOT NULL,    -- Product price
    Sold INT NOT NULL,                -- Number of items sold
    Category NVARCHAR(255) NOT NULL,  -- Product category
    Quantity INT NOT NULL             -- Stock quantity
);
GO

-- Create Feedbacks table
CREATE TABLE Feedbacks (
    ID_Product INT,                           -- Foreign key from Products
    ID_Customer INT,                          -- Foreign key from Customers
    Content NVARCHAR(MAX) NOT NULL,           -- Feedback content
    SentScore INT NOT NULL,                   -- Sentiment score
    SentLabel NVARCHAR(50) NOT NULL,          -- Sentiment label (negative, neutral, positive)
    PRIMARY KEY (ID_Product, ID_Customer),    -- Primary key
    FOREIGN KEY (ID_Product) REFERENCES Products(ID),   -- Set foreign key to Products table
    FOREIGN KEY (ID_Customer) REFERENCES Customers(ID)  -- Set foreign key to Customers table
);
GO

-- Create HistoryOfTransactions table
CREATE TABLE HistoryOfTransactions (
    ID_Customer INT,                          -- Foreign key from Customers
    ID_Product INT,                           -- Foreign key from Products
    Time DATETIME NOT NULL,                   -- Transaction time
    Quantity INT NOT NULL,                    -- Purchase quantity
    PRIMARY KEY (ID_Customer, ID_Product, Time),  -- Primary key includes ID_Customer, ID_Product, and Time
    FOREIGN KEY (ID_Customer) REFERENCES Customers(ID),   -- Foreign key to Customers table
    FOREIGN KEY (ID_Product) REFERENCES Products(ID)      -- Foreign key to Products table
);
GO

-- Create HistoryOfSearches table
CREATE TABLE HistoryOfSearches (
    ID_Customer INT,                          -- Foreign key from Customers
    Time DATETIME NOT NULL,                   -- Search time
    Content NVARCHAR(MAX) NOT NULL,           -- Search content
    Category NVARCHAR(255),                   -- Search category
    PRIMARY KEY (ID_Customer, Time),          -- Primary key
    FOREIGN KEY (ID_Customer) REFERENCES Customers(ID)   -- Foreign key to Customers table
);
GO
