-- ==============================================
-- RESTAURANT MANAGEMENT SYSTEM
-- III. Database Security and Administration
-- ==============================================

-- 1. Create roles
CREATE ROLE 'admin_role', 'cashier_role', 'waiter_role';

-- 2. Assign permissions to Waiter (Only allowed to view menu, view/update tables, and make reservations)
GRANT SELECT ON RestaurantManagement.MenuItems TO 'waiter_role';
GRANT SELECT, UPDATE ON RestaurantManagement.Tables TO 'waiter_role';
GRANT SELECT, INSERT, UPDATE ON RestaurantManagement.Reservations TO 'waiter_role';

-- 3. Assign permissions to Cashier (Allowed to work with invoices, tables, customers, and view dish details)
GRANT SELECT, INSERT, UPDATE ON RestaurantManagement.Customers TO 'cashier_role';
GRANT SELECT, INSERT, UPDATE ON RestaurantManagement.Invoices TO 'cashier_role';
GRANT SELECT, INSERT ON RestaurantManagement.InvoiceDetails TO 'cashier_role';
GRANT SELECT ON RestaurantManagement.MenuItems TO 'cashier_role';
GRANT SELECT, UPDATE ON RestaurantManagement.Tables TO 'cashier_role';

-- 4. Assign permissions to Admin (Full privileges on the entire database)
GRANT ALL PRIVILEGES ON RestaurantManagement.* TO 'admin_role';

-- 5. Create sample users and assign corresponding roles
CREATE USER 'nguyenvana'@'localhost' IDENTIFIED BY 'password123';
GRANT 'waiter_role' TO 'nguyenvana'@'localhost';
SET DEFAULT ROLE 'waiter_role' TO 'nguyenvana'@'localhost';

CREATE USER 'tranb'@'localhost' IDENTIFIED BY 'cashier_pass';
GRANT 'cashier_role' TO 'tranb'@'localhost';
SET DEFAULT ROLE 'cashier_role' TO 'tranb'@'localhost';

-- Create a view so that employees only see the masked phone number (Masking)
-- Instead of seeing 0912345678, they will see ******5678
CREATE VIEW vw_SecureCustomerData AS
SELECT 
    CustomerID,
    CustomerName,
    CONCAT('******', RIGHT(PhoneNumber, 4)) AS MaskedPhoneNumber,
    Address
FROM Customers;

-- The EXPLAIN command is used to analyze whether the Query is using an Index
EXPLAIN SELECT * FROM Reservations 
WHERE DateTime BETWEEN '2026-05-01 00:00:00' AND '2026-05-31 23:59:59' 
AND CustomerID = 5;