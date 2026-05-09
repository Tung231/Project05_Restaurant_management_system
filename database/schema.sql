-- ==============================================
-- RESTAURANT MANAGEMENT SYSTEM - DATABASE SCHEMA
-- ==============================================

-- 1. Creating and Using Databases
CREATE DATABASE IF NOT EXISTS RestaurantManagement;
USE RestaurantManagement;

-- ==========================================
-- CATEGORY GROUP (MASTER DATA)
-- Must be created first because other tables will reference it.
-- ==========================================

-- 2. Categories (Food Classification)
CREATE TABLE Categories (
    CategoryID INT AUTO_INCREMENT PRIMARY KEY,
    CategoryName VARCHAR(100) NOT NULL,
    Description TEXT
);

-- 3. Menu Items Table
CREATE TABLE MenuItems (
    DishID INT AUTO_INCREMENT PRIMARY KEY,
    DishName VARCHAR(255) NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    CategoryID INT NOT NULL,
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
);

-- 4. Customers table
CREATE TABLE Customers (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerName VARCHAR(255) NOT NULL,
    PhoneNumber VARCHAR(20) NOT NULL,
    Address VARCHAR(255)
);

-- 5. Tables (Dining tables)
CREATE TABLE Tables (
    TableID INT AUTO_INCREMENT PRIMARY KEY,
    TableNumber VARCHAR(10) NOT NULL UNIQUE,
    Capacity INT NOT NULL,
    Status VARCHAR(50) NOT NULL DEFAULT 'Available' 
    -- Status: Available, Reserved, Occupied
);

-- 6. Staff Table
CREATE TABLE Staff (
    StaffID INT AUTO_INCREMENT PRIMARY KEY,
    FullName VARCHAR(255) NOT NULL,
    Role VARCHAR(50) NOT NULL, 
    -- Role: Admin, Cashier, Waiter
    PhoneNumber VARCHAR(20)
);

-- ==========================================
-- TRANSACTIONAL DATA
-- Contains foreign keys referencing the Category Group
-- ==========================================

-- 7. Reservations Table
CREATE TABLE Reservations (
    ReservationID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    TableID INT NOT NULL,
    DateTime DATETIME NOT NULL,
    GuestCount INT NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (TableID) REFERENCES Tables(TableID)
);

-- 8. Invoices Table 
CREATE TABLE Invoices (
    InvoiceID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    TableID INT NOT NULL,
    StaffID INT NOT NULL,
    ReservationID INT, -- Intentionally set to NULLABLE for walk-in customers who do not make a reservation.
    TotalAmount DECIMAL(12, 2) DEFAULT 0.00,
    PaymentDate DATETIME,
    PaymentMethod VARCHAR(50), 
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (TableID) REFERENCES Tables(TableID),
    FOREIGN KEY (StaffID) REFERENCES Staff(StaffID),
    FOREIGN KEY (ReservationID) REFERENCES Reservations(ReservationID)
);

-- 9. InvoiceDetails Table
CREATE TABLE InvoiceDetails (
    InvoiceDetailID INT AUTO_INCREMENT PRIMARY KEY,
    InvoiceID INT NOT NULL,
    DishID INT NOT NULL,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10, 2) NOT NULL, 
    -- Save the price at the time of sale, in case MenuItems changes prices later.
    FOREIGN KEY (InvoiceID) REFERENCES Invoices(InvoiceID),
    FOREIGN KEY (DishID) REFERENCES MenuItems(DishID)
);
