import os
import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
fake = Faker('vi_VN')

def seed_database():
    try:
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "RestaurantManagement"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "")
        )
        cursor = db.cursor()
        print("✅ Đã kết nối Database! Bắt đầu dọn dẹp và bơm dữ liệu...")

        # ==========================================
        # 0. DỌN DẸP SẠCH SẼ DỮ LIỆU CŨ (TRUNCATE)
        # ==========================================
        print("🧹 Đang dọn dẹp dữ liệu cũ (Reset ID về 1)...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;") # Tạm tắt kiểm tra khóa ngoại để xóa
        
        tables_to_truncate = ["InvoiceDetails", "Invoices", "Reservations", "MenuItems", "Categories", "Customers", "Staff", "Tables"]
        for table in tables_to_truncate:
            try:
                cursor.execute(f"TRUNCATE TABLE {table}")
            except Exception as e:
                pass # Bỏ qua nếu bảng chưa tồn tại
                
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;") # Bật lại khóa ngoại

        # ==========================================
        # 1. BẢNG KHÔNG PHỤ THUỘC (Categories, Tables, Staff, Customers)
        # ==========================================
        
        # 1.1 - Categories (10 nhóm)
        print("⏳ Đang bơm Categories (10)...")
        categories = ["Món Nước", "Cơm & Món Chính", "Khai Vị", "Ăn Vặt", "Đồ Uống", "Lẩu", "Nướng", "Hải Sản", "Món Chay", "Tráng Miệng"]
        for cat in categories:
            cursor.execute("INSERT INTO Categories (CategoryName, Description) VALUES (%s, %s)", (cat, f'Nhóm {cat} ngon miệng và hấp dẫn.'))
        
        # 1.2 - Tables (25 Bàn)
        print("⏳ Đang bơm Tables (25)...")
        for i in range(1, 26):
            capacity = random.choice([2, 4, 4, 6, 8, 10])
            status = random.choice(['Available', 'Available', 'Reserved', 'Occupied'])
            cursor.execute("INSERT INTO Tables (TableNumber, Capacity, Status) VALUES (%s, %s, %s)", (f"Bàn {i}", capacity, status))

        # 1.3 - Staff (12 Nhân viên)
        print("⏳ Đang bơm Staff (12)...")
        roles = ["Quản lý", "Bếp trưởng", "Đầu bếp", "Pha chế", "Thu ngân"] + ["Phục vụ"] * 7
        for role in roles:
            cursor.execute("INSERT INTO Staff (FullName, Role, PhoneNumber) VALUES (%s, %s, %s)", (fake.name(), role, fake.phone_number()))

        # 1.4 - Customers (100 Khách hàng)
        print("⏳ Đang bơm Customers (100)...")
        # Danh sách đường và quận quen thuộc
        streets = ["Trần Đại Nghĩa", "Giải Phóng", "Lê Thanh Nghị", "Đại La", "Minh Khai", "Bạch Mai", "Tạ Quang Bửu", "Hai Bà Trưng", "Phố Vọng", "Trương Định"]
        districts = ["Hai Bà Trưng", "Đống Đa", "Hoàn Kiếm", "Ba Đình", "Cầu Giấy", "Thanh Xuân", "Hoàng Mai"]

        for _ in range(100):
            # Tạo số điện thoại chuẩn VN: Đầu 03, 08, 09 + 8 số ngẫu nhiên
            phone = f"0{random.choice(['3', '8', '9'])}{random.randint(10000000, 99999999)}"
            
            # Tạo địa chỉ chuẩn 
            address = f"Số {random.randint(1, 200)} {random.choice(streets)}, Quận {random.choice(districts)}, Hà Nội"
            
            cursor.execute("INSERT INTO Customers (CustomerName, PhoneNumber, Address) VALUES (%s, %s, %s)", 
                           (fake.name(), phone, address))
        db.commit()

        # ==========================================
        # 2. BẢNG PHỤ THUỘC MỨC 1 (MenuItems)
        # ==========================================
        
        # 2.1 - MenuItems (20 Món Cực Chuẩn)
        print("⏳ Đang bơm MenuItems (20)...")
        menu_items = [
            # 1. Khai vị
            ("Gỏi Cuốn", 35000, 3, "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=600&h=400&fit=crop"),
            ("Súp", 30000, 3, "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=600&h=400&fit=crop"),
            
            # 2. Món nước
            ("Phở Bò", 45000, 1, "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=600&h=400&fit=crop"),
            ("Bún Riêu", 40000, 1, "https://images.unsplash.com/photo-1555126634-323283e090fa?w=600&h=400&fit=crop"),
            
            # 3. Món chính
            ("Cơm Tấm", 50000, 2, "https://images.unsplash.com/photo-1574484284002-952d92456975?w=600&h=400&fit=crop"),
            ("Cơm Chiên Trứng", 40000, 2, "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=600&h=400&fit=crop"),
            
            # 4. Ăn vặt
            ("Khoai Tây Chiên", 30000, 4, "https://images.unsplash.com/photo-1576107232684-1279f390859f?w=600&h=400&fit=crop"),
            ("Nem Chua Rán", 45000, 4, "https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?w=600&h=400&fit=crop"),
            
            # 5. Đồ uống
            ("Trà Đá", 10000, 5, "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=600&h=400&fit=crop"),
            ("Nước Chanh", 20000, 5, "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600&h=400&fit=crop"),
            
            # 6. Lẩu
            ("Lẩu Thái", 250000, 6, "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=600&h=400&fit=crop"),
            ("Lẩu Gà Lá Giang", 220000, 6, "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=600&h=400&fit=crop"),
            
            # 7. Nướng
            ("Thịt Ba Chỉ Nướng", 120000, 7, "https://images.unsplash.com/photo-1558030006-450675393462?w=600&h=400&fit=crop"),
            ("Mực Nướng Sa Tế", 150000, 7, "https://images.unsplash.com/photo-1599084993091-1cb5c0721cc6?w=600&h=400&fit=crop"),
            
            # 8. Hải sản
            ("Tôm Hấp", 180000, 8, "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?w=600&h=400&fit=crop"),
            ("Ngao Hấp", 80000, 8, "https://images.unsplash.com/photo-1560717845-968823efbee1?w=600&h=400&fit=crop"),
            
            # 9. Món chay
            ("Đậu Hũ Chiên Sả Ớt", 35000, 9, "https://images.unsplash.com/photo-1564834724105-918b73d1b9e0?w=600&h=400&fit=crop"),
            ("Rau Muống Xào Tỏi", 30000, 9, "https://images.unsplash.com/photo-1565557615-38b4d8d15024?w=600&h=400&fit=crop"),
            
            # 10. Tráng miệng
            ("Chè Đậu Xanh", 20000, 10, "https://images.unsplash.com/photo-1551024601-bec78aea704b?w=600&h=400&fit=crop"),
            ("Dưa Hấu", 25000, 10, "https://images.unsplash.com/photo-1587314168485-3236d6710814?w=600&h=400&fit=crop")
        ]
        
        for item in menu_items:
            cursor.execute("INSERT INTO MenuItems (DishName, Price, CategoryID, ImageURL) VALUES (%s, %s, %s, %s)", item)
        db.commit()

        # ==========================================
        # 3. BẢNG PHỤ THUỘC GIAO DỊCH (Reservations, Invoices, InvoiceItems)
        # ==========================================

        # 3.1 - Reservations (150 Đặt bàn)
        print("⏳ Đang bơm Reservations (150)...")
        for _ in range(150):
            cust_id = random.randint(1, 100)
            table_id = random.randint(1, 25)
            # Đảm bảo bàn đó là trống trước khi tạo đặt bàn
            cursor.execute("UPDATE Tables SET Status = 'Available' WHERE TableID = %s", (table_id,))
            # Tạo ngày đặt ngẫu nhiên trong vòng 30 ngày qua và 10 ngày tới
            res_date = datetime.now() - timedelta(days=random.randint(-10, 30))
            res_date = res_date.replace(hour=random.randint(10, 21), minute=random.choice([0, 15, 30, 45]), second=0)
            guests = random.randint(2, 10)
            cursor.execute("INSERT INTO Reservations (CustomerID, TableID, DateTime, GuestCount) VALUES (%s, %s, %s, %s)", 
                           (cust_id, table_id, res_date.strftime('%Y-%m-%d %H:%M:%S'), guests))

        # 3.2 - Invoices (150 Hóa đơn) & InvoiceItems (~500 Chi tiết)
        print("⏳ Đang bơm Invoices & InvoiceItems...")
        for inv_id in range(1, 151):
            cust_id = random.randint(1, 100)
            staff_id = random.randint(1, 12)
            inv_date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            # Tính tổng tiền hóa đơn
            total_amount = 0
            invoice_items_count = random.randint(2, 5) # Mỗi hóa đơn có 2 đến 5 món
            items_to_insert = []
            
            for _ in range(invoice_items_count):
                dish = random.choice(menu_items) # Chọn ngẫu nhiên từ 20 món
                dish_id = menu_items.index(dish) + 1
                price = dish[1]
                qty = random.randint(1, 3)
                total_amount += price * qty
                items_to_insert.append((inv_id, dish_id, qty, price))

            # 🌟 Tạo tỷ lệ random: 75% Chuyển khoản (Transfer), 25% Tiền mặt (Cash)
            payment_method = random.choices(['Transfer', 'Cash'], weights=[75, 25], k=1)[0]

            # Lưu Hóa đơn với phương thức thanh toán vừa tạo
            cursor.execute("INSERT INTO Invoices (CustomerID, TableID, StaffID, ReservationID, TotalAmount, PaymentDate, PaymentMethod) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                           (cust_id, random.randint(1, 25), staff_id, None, total_amount, inv_date.strftime('%Y-%m-%d %H:%M:%S'), payment_method))
            
            # Lưu Chi tiết Hóa đơn
            for item in items_to_insert:
                cursor.execute("INSERT INTO InvoiceDetails (InvoiceID, DishID, Quantity, UnitPrice) VALUES (%s, %s, %s, %s)", item)
                
        db.commit()

        print("\n🎉 XUẤT SẮC! Toàn bộ hệ thống CSDL đã được nạp dữ liệu chuẩn chỉnh:")
        print("   - 10 Danh mục | 20 Món ăn | 100 Khách hàng | 25 Bàn | 12 Nhân viên")
        print("   - 150 Lượt đặt bàn | 150 Hóa đơn | Khoảng 500 Chi tiết hóa đơn")

    except mysql.connector.Error as err:
        print(f"❌ LỖI RỒI: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

if __name__ == "__main__":
    seed_database()