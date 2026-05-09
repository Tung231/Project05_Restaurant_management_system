-- ==============================================
-- RESTAURANT MANAGEMENT SYSTEM
-- Advanced Database Objects
-- ==============================================

# 1. Indexes 
-- Optimize food lookup
CREATE INDEX idx_dish_name ON MenuItems(DishName);
CREATE INDEX idx_dish_category ON MenuItems(CategoryID);

-- Optimize reservation search by date and customer
CREATE INDEX idx_res_datetime ON Reservations(DateTime);
CREATE INDEX idx_res_customer ON Reservations(CustomerID);

# 2. Views
-- View 1: Daily bookings
CREATE VIEW vw_DailyBookings AS
SELECT 
    DATE(r.DateTime) AS BookingDate,
    TIME(r.DateTime) AS BookingTime,
    c.CustomerName, 
    c.PhoneNumber,
    t.TableNumber, 
    r.GuestCount
FROM Reservations r
JOIN Customers c ON r.CustomerID = c.CustomerID
JOIN Tables t ON r.TableID = t.TableID
ORDER BY r.DateTime;

-- View 2: Table availability status
CREATE VIEW vw_TableAvailability AS
SELECT TableID, TableNumber, Status
FROM Tables
WHERE Status = 'Available';

-- View 3: Top-selling dishes
CREATE VIEW vw_TopSellingDishes AS
SELECT 
    m.DishID, 
    m.DishName, 
    SUM(id.Quantity) AS TotalQuantitySold,
    SUM(id.Quantity * id.UnitPrice) AS TotalRevenue
FROM MenuItems m
JOIN InvoiceDetails id ON m.DishID = id.DishID
GROUP BY m.DishID, m.DishName
ORDER BY TotalQuantitySold DESC;

-- 3. User Defined Functions
-- Function to calculate final amount with service charges or discounts dynamically
DELIMITER //

CREATE FUNCTION udf_CalculateFinalAmount(
    subTotal DECIMAL(12, 2),
    discountPercent DECIMAL(5, 2),
    serviceChargePercent DECIMAL(5, 2)
) 
RETURNS DECIMAL(12, 2)
DETERMINISTIC
BEGIN
    DECLARE finalAmount DECIMAL(12, 2);
    -- Formula: Final Amount = Subtotal - Discount + Service Charge
    SET finalAmount = subTotal - (subTotal * discountPercent / 100) + (subTotal * serviceChargePercent / 100);
    RETURN finalAmount;
END //

DELIMITER ;

-- 4. Stored Procedures
-- SP 1: Confirm reservation (Automate reservation confirmation)[cite: 1]
-- This procedure adds a new reservation record. The table status will be updated by a Trigger.
DELIMITER //

CREATE PROCEDURE sp_ConfirmReservation(
    IN p_CustomerID INT,
    IN p_TableID INT,
    IN p_DateTime DATETIME,
    IN p_GuestCount INT
)
BEGIN
    INSERT INTO Reservations (CustomerID, TableID, DateTime, GuestCount)
    VALUES (p_CustomerID, p_TableID, p_DateTime, p_GuestCount);
END //

DELIMITER ;

-- SP 2: Calculate bills (Automate bill generation)
-- Connect with InvoiceDetails table to calculate TotalAmount
DELIMITER //

CREATE PROCEDURE sp_GenerateBill(
    IN p_InvoiceID INT,
    IN p_Discount DECIMAL(5,2),
    IN p_ServiceCharge DECIMAL(5,2)
)
BEGIN
    DECLARE v_SubTotal DECIMAL(12,2);
    DECLARE v_FinalTotal DECIMAL(12,2);
    
    -- Subtotal calculated from the items the customer has ordered.
    SELECT SUM(Quantity * UnitPrice) INTO v_SubTotal
    FROM InvoiceDetails
    WHERE InvoiceID = p_InvoiceID;
    
    -- Process if the bill doesn't include any items.
    IF v_SubTotal IS NULL THEN
        SET v_SubTotal = 0;
    END IF;
    
    -- Call the UDF created above to calculate the final amount.
    SET v_FinalTotal = udf_CalculateFinalAmount(v_SubTotal, p_Discount, p_ServiceCharge);
    
    -- Update the total amount in the original invoice.
    UPDATE Invoices
    SET TotalAmount = v_FinalTotal
    WHERE InvoiceID = p_InvoiceID;
    
END //

DELIMITER ;

-- 5. Triggers

-- Trigger 1: Auto-update table status after reservation 
DELIMITER //

CREATE TRIGGER trg_AfterReservationInsert
AFTER INSERT ON Reservations
FOR EACH ROW
BEGIN
    UPDATE Tables
    SET Status = 'Reserved'
    WHERE TableID = NEW.TableID;
END //

DELIMITER ;

-- Trigger 2: Auto-update table status after payment
DELIMITER //

CREATE TRIGGER trg_AfterInvoicePayment
AFTER UPDATE ON Invoices
FOR EACH ROW
BEGIN
    -- Check if the PaymentDate column has been updated from NULL to a value (i.e., the invoice has been paid)
    IF NEW.PaymentDate IS NOT NULL AND OLD.PaymentDate IS NULL THEN
        UPDATE Tables
        SET Status = 'Available'
        WHERE TableID = NEW.TableID;
    END IF;
END //

DELIMITER ;
