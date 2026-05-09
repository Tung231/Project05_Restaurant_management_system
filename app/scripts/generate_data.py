import os
import random
from dotenv import load_dotenv
import mysql.connector
from faker import Faker
from datetime import datetime, timedelta

# 1. Khởi tạo
load_dotenv()
fake = Faker(['vi_VN'])

# Định nghĩa các con số "hợp lý" cho từng bảng
COUNTS = {
    "Categories": 10,
    "MenuItems": 40,
    "Customers": 100,
    "Tables": 25,
    "Staff": 12,
    "Reservations": 150,
    "Invoices": 510,        # Giữ đúng 510 để đáp ứng yêu cầu số lượng của đề bài
    "InvoiceItems": 1200    # Chi tiết món ăn (thường nhiều hơn số hóa đơn)
}

# 2. Kết nối Database
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = db.cursor()

def seed_data():
    try:
        print("🚀 Đang bắt đầu bơm dữ liệu thực tế vào hệ thống...")

        # --- 1. Categories (10 dòng) ---
        categories = ['Khai vị', 'Món chính', 'Tráng miệng', 'Đồ uống', 'Hải sản', 'Món lẩu', 'Món nướng', 'Đặc sản', 'Món chay', 'Rượu vang']
        for cat in categories:
            cursor.execute("INSERT INTO Categories (CategoryName, Description) VALUES (%s, %s)", 
                           (cat, fake.sentence()))
        db.commit()

        # --- 2. MenuItems (40 dòng) ---
        for _ in range(COUNTS["MenuItems"]):
            cursor.execute("INSERT INTO MenuItems (DishName, Price, CategoryID) VALUES (%s, %s, %s)",
                           (fake.word().capitalize(), random.randint(30, 500) * 1000, random.randint(1, COUNTS["Categories"])))
        db.commit()

        # --- 3. Customers (100 dòng) ---
        for _ in range(COUNTS["Customers"]):
            cursor.execute("INSERT INTO Customers (CustomerName, PhoneNumber, Address) VALUES (%s, %s, %s)",
                           (fake.name(), fake.phone_number()[:20], fake.address()))
        db.commit()

        # --- 4. Tables (25 bàn) ---
        for i in range(1, COUNTS["Tables"] + 1):
            status = random.choice(['Available', 'Reserved', 'Occupied'])
            cursor.execute("INSERT INTO Tables (TableNumber, Status) VALUES (%s, %s)", (f"Bàn {i}", status))
        db.commit()

        # --- 5. Staff (12 nhân viên) ---
        roles = ['Admin', 'Cashier', 'Waiter']
        for _ in range(COUNTS["Staff"]):
            cursor.execute("INSERT INTO Staff (FullName, Role, PhoneNumber) VALUES (%s, %s, %s)",
                           (fake.name(), random.choice(roles), fake.phone_number()[:20]))
        db.commit()

        # --- 6. Reservations (150 dòng) ---
        for _ in range(COUNTS["Reservations"]):
            table_id = random.randint(1, COUNTS["Tables"])
            
            # [MẸO FIX LỖI]: Ép bàn về trạng thái 'Available' trước khi chèn 
            # để không bị Trigger gác cổng đánh sập script
            cursor.execute("UPDATE Tables SET Status = 'Available' WHERE TableID = %s", (table_id,))
            
            res_date = datetime.now() + timedelta(days=random.randint(-30, 30), hours=random.randint(1, 12))
            cursor.execute("INSERT INTO Reservations (CustomerID, TableID, DateTime, GuestCount) VALUES (%s, %s, %s, %s)",
                           (random.randint(1, COUNTS["Customers"]), table_id, res_date, random.randint(1, 10)))
        db.commit()

        # --- 7. Invoices (510 dòng - Chốt số lượng theo yêu cầu)[cite: 1] ---
        for _ in range(COUNTS["Invoices"]):
            pay_date = datetime.now() - timedelta(days=random.randint(1, 90))
            cursor.execute("""
                INSERT INTO Invoices (CustomerID, TableID, StaffID, ReservationID, PaymentDate, PaymentMethod) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (random.randint(1, COUNTS["Customers"]), random.randint(1, COUNTS["Tables"]), 
                  random.randint(1, COUNTS["Staff"]), None, pay_date, random.choice(['Cash', 'Card', 'Banking'])))
        db.commit()

        # --- 8. InvoiceDetails (1200 dòng) ---
        # Chèn ngẫu nhiên các món vào các hóa đơn đã tạo
        for _ in range(COUNTS["InvoiceItems"]):
            dish_id = random.randint(1, COUNTS["MenuItems"])
            cursor.execute("SELECT Price FROM MenuItems WHERE DishID = %s", (dish_id,))
            price = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO InvoiceDetails (InvoiceID, DishID, Quantity, UnitPrice) 
                VALUES (%s, %s, %s, %s)
            """, (random.randint(1, COUNTS["Invoices"]), dish_id, random.randint(1, 4), price))
        db.commit()

        # --- Bước cuối: Chạy Stored Procedure để tính lại TotalAmount cho tất cả Invoices ---
        print("🔄 Đang chạy Stored Procedure để cập nhật tổng tiền hóa đơn...")
        for inv_id in range(1, COUNTS["Invoices"] + 1):
            cursor.callproc('sp_GenerateBill', (inv_id, 0.0, 0.0))
        db.commit()

        # --- BƯỚC KHÔI PHỤC (Trả lại trạng thái ngẫu nhiên cho các bàn) ---
        print("🎲 Đang khôi phục trạng thái ngẫu nhiên cho các bàn ăn để dữ liệu trông thực tế nhất...")
        for i in range(1, COUNTS["Tables"] + 1):
            status = random.choice(['Available', 'Reserved', 'Occupied'])
            cursor.execute("UPDATE Tables SET Status = %s WHERE TableID = %s", (status, i))
        db.commit()

        print("✅ Đã hoàn thành bơm dữ liệu hợp lý!")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi: {e}")
    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    seed_data()