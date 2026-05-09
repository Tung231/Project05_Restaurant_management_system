from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from mysql.connector.connection import MySQLConnection
from app.core.database import get_db
from datetime import datetime 

# Khai báo nơi chứa các file HTML
templates = Jinja2Templates(directory="app/templates")

router = APIRouter(tags=["Web Interface"])

def generate_menu_image_url(dish_name, category=None):
    keyword = category if category else dish_name
    keyword = keyword.replace(' ', '+')
    return f"https://source.unsplash.com/600x400/?{keyword},food"

@router.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/login")

# Render trang Login
@router.get("/login", include_in_schema=False)
def render_login(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="login.html", 
        context={"request": request}
    )

@router.get("/menu", include_in_schema=False)
def render_customer_menu(request: Request, db: MySQLConnection = Depends(get_db)):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT m.DishID, m.DishName, m.Price, m.ImageURL, c.CategoryName "
            "FROM MenuItems m LEFT JOIN Categories c ON m.CategoryID = c.CategoryID "
            "ORDER BY m.CategoryID, m.DishID DESC"
        )
        items = cursor.fetchall()
        cursor.close()
        
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"request": request, "items": items}
        )
    except Exception as e:
        return {"error": str(e), "message": "Kiểm tra lại cấu trúc bảng MenuItems"}

@router.get("/tables", include_in_schema=False)
def render_tables(request: Request, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT TableID, TableNumber, Capacity, Status FROM Tables ORDER BY TableNumber")
    tables = cursor.fetchall()
    cursor.close()
    return templates.TemplateResponse(
        request=request,
        name="tables.html",
        context={"request": request, "tables": tables}
    )

@router.get("/admin/customers", include_in_schema=False)
def render_admin_customers(request: Request, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT CustomerID, CustomerName, PhoneNumber, Address FROM Customers ORDER BY CustomerID DESC")
    customers = cursor.fetchall()
    cursor.close()
    return templates.TemplateResponse(
        request=request,
        name="admin_customers.html",
        context={"request": request, "customers": customers}
    )

@router.get("/admin/tables", include_in_schema=False)
def render_admin_tables(request: Request, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT TableID, TableNumber, Capacity, Status 
        FROM Tables 
        ORDER BY 
            FIELD(Status, 'Occupied', 'Reserved', 'Available'), 
            CAST(SUBSTRING_INDEX(TableNumber, ' ', -1) AS UNSIGNED)
    """)
    tables = cursor.fetchall()
    cursor.close()
    return templates.TemplateResponse(
        request=request,
        name="admin_tables.html",  
        context={"request": request, "tables": tables}
    )

@router.get("/admin/menu", include_in_schema=False)
def render_admin_menu(request: Request, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryName")
    categories = cursor.fetchall()
    cursor.execute("""
        SELECT m.DishID, m.DishName, m.Price, m.IsAvailable, c.CategoryName, m.CategoryID 
        FROM MenuItems m 
        LEFT JOIN Categories c ON m.CategoryID = c.CategoryID 
        ORDER BY m.DishID DESC
    """)
    menu_items = cursor.fetchall()
    cursor.close()
    return templates.TemplateResponse(
        request=request,
        name="admin_menu.html",
        context={"request": request, "categories": categories, "menu_items": menu_items}
    )

@router.get("/admin/reservations", include_in_schema=False)
def render_admin_reservations(request: Request, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT r.ReservationID, c.CustomerID, c.CustomerName, t.TableID, t.TableNumber, t.Capacity, r.GuestCount, r.Notes,
               DATE_FORMAT(r.DateTime, '%d/%m/%Y %h:%i %p') AS FormattedTime,
               DATE_FORMAT(r.DateTime, '%Y-%m-%dT%H:%i') AS RawDateTime
        FROM Reservations r
        JOIN Customers c ON r.CustomerID = c.CustomerID
        JOIN Tables t ON r.TableID = t.TableID
        ORDER BY r.DateTime DESC
    """)
    reservations = cursor.fetchall()
    
    cursor.execute("""
        SELECT TableID, TableNumber, Capacity 
        FROM Tables 
        ORDER BY CAST(SUBSTRING_INDEX(TableNumber, ' ', -1) AS UNSIGNED)
    """)
    tables = cursor.fetchall()
    
    cursor.execute("SELECT CustomerID, CustomerName, PhoneNumber FROM Customers ORDER BY CustomerName")
    customers = cursor.fetchall()

    cursor.execute("""
        SELECT r.TableID, c.CustomerName, DATE_FORMAT(r.DateTime, '%H:%i %d/%m/%Y') AS FormattedTime
        FROM Reservations r
        JOIN Customers c ON r.CustomerID = c.CustomerID
        WHERE r.DateTime >= CURDATE()
        ORDER BY r.DateTime ASC
    """)
    future_res = cursor.fetchall()
    
    cursor.close()
    return templates.TemplateResponse(
        request=request, name="admin_reservations.html", 
        context={"request": request, "reservations": reservations, "tables": tables, "customers": customers, "future_res": future_res}
    )

@router.get("/admin/invoices", include_in_schema=False)
def render_admin_invoices(request: Request, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    
    # 1. Lấy danh sách hóa đơn (ĐÃ SỬA ORDER BY ĐỂ SẮP XẾP THEO NGÀY GIỜ TRƯỚC)
    cursor.execute("""
        SELECT i.InvoiceID, c.CustomerID, c.CustomerName, t.TableID, t.TableNumber, 
               i.TotalAmount, i.PaymentMethod, DATE_FORMAT(i.PaymentDate, '%d/%m/%Y %H:%i') AS FormattedDate,
               s.FullName AS StaffName
        FROM Invoices i
        JOIN Customers c ON i.CustomerID = c.CustomerID
        JOIN Tables t ON i.TableID = t.TableID
        LEFT JOIN staff s ON i.StaffID = s.StaffID
        ORDER BY i.PaymentDate DESC, i.InvoiceID DESC
    """)
    invoices = cursor.fetchall()
    
    # 2. Khách hàng
    cursor.execute("SELECT CustomerID, CustomerName FROM Customers ORDER BY CustomerName")
    customers = cursor.fetchall()
    
    # 3. Bàn
    cursor.execute("""
        SELECT TableID, TableNumber 
        FROM Tables 
        ORDER BY CAST(SUBSTRING_INDEX(TableNumber, ' ', -1) AS UNSIGNED)
    """)
    tables = cursor.fetchall()

    # Lấy danh sách Thực đơn để đổ vào form Tạo hóa đơn
    cursor.execute("SELECT DishID, DishName, Price FROM MenuItems WHERE IsAvailable = 1 ORDER BY DishName")
    menu_items = cursor.fetchall()
    
    cursor.close()
    
    return templates.TemplateResponse(
        request=request, name="admin_invoices.html", 
        context={"request": request, "invoices": invoices, "customers": customers, "tables": tables, "menu_items": menu_items}
    )

@router.get("/admin/dashboard", include_in_schema=False)
def render_admin_dashboard(request: Request, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    
    # 1. Các con số tổng quan
    cursor.execute("SELECT COUNT(*) AS total_customers FROM Customers")
    total_customers = cursor.fetchone()["total_customers"]
    
    cursor.execute("SELECT COUNT(*) AS total_tables FROM Tables")
    total_tables = cursor.fetchone()["total_tables"]
    
    cursor.execute("SELECT COUNT(*) AS total_menu FROM MenuItems")
    total_menu = cursor.fetchone()["total_menu"]
    
    cursor.execute("SELECT COUNT(*) AS total_reservations FROM Reservations")
    total_reservations = cursor.fetchone()["total_reservations"]
    
    cursor.execute("SELECT COALESCE(SUM(TotalAmount), 0) AS total_revenue FROM Invoices")
    total_revenue = cursor.fetchone()["total_revenue"]
    
    cursor.execute("SELECT m.DishName, SUM(id.Quantity) AS total_sold FROM MenuItems m JOIN InvoiceDetails id ON m.DishID = id.DishID GROUP BY m.DishName ORDER BY total_sold DESC LIMIT 1")
    top_dish = cursor.fetchone()

    # 2. Dữ liệu biểu đồ Món ăn
    cursor.execute("SELECT m.DishName, SUM(id.Quantity) AS total_sold FROM MenuItems m JOIN InvoiceDetails id ON m.DishID = id.DishID GROUP BY m.DishName ORDER BY total_sold DESC LIMIT 5")
    top_5_dishes = cursor.fetchall()
    chart_labels = [row["DishName"] for row in top_5_dishes]
    chart_values = [int(row["total_sold"]) for row in top_5_dishes]

    # 3. Dữ liệu biểu đồ Doanh thu theo tháng
    cursor.execute("""
        SELECT DATE_FORMAT(PaymentDate, '%m/%Y') AS MonthLabel, 
               DATE_FORMAT(PaymentDate, '%Y-%m') AS MonthSort, 
               SUM(TotalAmount) AS MonthlyRevenue 
        FROM Invoices 
        GROUP BY MonthLabel, MonthSort 
        ORDER BY MonthSort ASC
    """)
    monthly_data = cursor.fetchall()
    revenue_labels = [row["MonthLabel"] for row in monthly_data]
    revenue_values = [int(row["MonthlyRevenue"]) for row in monthly_data]

    # 4. Top 5 Khách hàng VIP
    cursor.execute("""
        SELECT c.CustomerName, COUNT(i.InvoiceID) AS VisitCount, SUM(i.TotalAmount) AS TotalSpend
        FROM Customers c
        JOIN Invoices i ON c.CustomerID = i.CustomerID
        GROUP BY c.CustomerID, c.CustomerName
        ORDER BY TotalSpend DESC
        LIMIT 5
    """)
    top_customers = cursor.fetchall()

    # 🌟 5. Thống kê tần suất sử dụng bàn (Dựa trên số lượng hóa đơn)
    cursor.execute("""
        SELECT t.TableNumber, COUNT(i.InvoiceID) AS UsageCount
        FROM Tables t
        JOIN Invoices i ON t.TableID = i.TableID
        GROUP BY t.TableID, t.TableNumber
        ORDER BY UsageCount DESC
        LIMIT 5
    """)
    table_usage = cursor.fetchall()
    table_labels = [row["TableNumber"] for row in table_usage]
    table_values = [int(row["UsageCount"]) for row in table_usage]

    cursor.close()
    
    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "request": request, "total_customers": total_customers, "total_tables": total_tables,
            "total_menu": total_menu, "total_reservations": total_reservations, "total_revenue": total_revenue,
            "top_dish": top_dish, "chart_labels": chart_labels, "chart_values": chart_values,
            "revenue_labels": revenue_labels, "revenue_values": revenue_values, 
            "top_customers": top_customers,
            "table_labels": table_labels, "table_values": table_values # 🌟 Truyền dữ liệu Bàn ra giao diện
        }
    )

# =========================================================
# TỔNG HỢP CÁC API XỬ LÝ DỮ LIỆU (CRUD)
# =========================================================

# ---------------------------------------------------------
# 1. API ĐĂNG NHẬP (Dành cho Lễ tân / Nhân viên)
# ---------------------------------------------------------
@router.post("/api/login", include_in_schema=False)
async def api_login(request: Request, db: MySQLConnection = Depends(get_db)):
    data = await request.json()
    phone = data.get('phone')
    password = data.get('password')
    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT StaffID, FullName, Role 
            FROM staff 
            WHERE PhoneNumber = %s AND Password = %s
        """, (phone, password))
        
        staff = cursor.fetchone()
        
        if staff:
            return {"status": "success", "staff": staff}
        else:
            return {"status": "error", "message": "Sai số điện thoại hoặc mật khẩu!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()

# ---------------------------------------------------------
# 2. CÁC API QUẢN LÝ KHÁCH HÀNG (CUSTOMERS)
# ---------------------------------------------------------
@router.post("/api/customers", include_in_schema=False)
async def api_create_customer(request: Request, db: MySQLConnection = Depends(get_db)):
    data = await request.json()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO Customers (CustomerName, PhoneNumber, Address) VALUES (%s, %s, %s)",
                       (data['name'], data['phone'], data['address']))
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()

@router.put("/api/customers/{cust_id}", include_in_schema=False)
async def api_update_customer(cust_id: int, request: Request, db: MySQLConnection = Depends(get_db)):
    data = await request.json()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE Customers SET CustomerName=%s, PhoneNumber=%s, Address=%s WHERE CustomerID=%s",
                       (data['name'], data['phone'], data['address'], cust_id))
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()

@router.delete("/api/customers/{cust_id}", include_in_schema=False)
def api_delete_customer(cust_id: int, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Customers WHERE CustomerID = %s", (cust_id,))
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": "Không thể xóa khách hàng này vì họ đã có lịch sử Đặt bàn hoặc Hóa đơn!"}
    finally:
        cursor.close()

# ---------------------------------------------------------
# 3. CÁC API QUẢN LÝ THỰC ĐƠN (MENU ITEMS)
# ---------------------------------------------------------
@router.post("/api/menu", include_in_schema=False)
async def api_create_menu(request: Request, db: MySQLConnection = Depends(get_db)):
    data = await request.json()
    cursor = db.cursor()
    try:
        img_url = f"https://source.unsplash.com/600x400/?{data['name'].replace(' ', '+')},food"
        cursor.execute("""
            INSERT INTO MenuItems (DishName, Price, CategoryID, IsAvailable, ImageURL)
            VALUES (%s, %s, %s, %s, %s)
        """, (data['name'], data['price'], data['category_id'], data['is_available'], img_url))
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()

@router.put("/api/menu/{dish_id}", include_in_schema=False)
async def api_update_menu(dish_id: int, request: Request, db: MySQLConnection = Depends(get_db)):
    data = await request.json()
    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE MenuItems 
            SET DishName=%s, Price=%s, CategoryID=%s, IsAvailable=%s
            WHERE DishID=%s
        """, (data['name'], data['price'], data['category_id'], data['is_available'], dish_id))
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()

@router.delete("/api/menu/{dish_id}", include_in_schema=False)
def api_delete_menu(dish_id: int, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM MenuItems WHERE DishID = %s", (dish_id,))
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": "Không thể xóa món ăn đã có trong hóa đơn của khách!"}
    finally:
        cursor.close()

# ---------------------------------------------------------
# 4. CÁC API QUẢN LÝ ĐẶT BÀN (RESERVATIONS) - CÓ BẢO VỆ CHỐNG TRÙNG LỊCH
# ---------------------------------------------------------
# 1. TẠO ĐẶT BÀN MỚI
@router.post("/api/reservations", include_in_schema=False)
async def api_create_reservation(request: Request, db: MySQLConnection = Depends(get_db)):
    data = await request.json()
    cursor = db.cursor(dictionary=True)
    try:
        # Làm sạch chuỗi thời gian (Xóa ký tự 'T' để MySQL hiểu chuẩn xác 100%)
        dt_str = data['datetime'].replace('T', ' ')
        
        cursor.execute("""
            SELECT c.CustomerName, DATE_FORMAT(r.DateTime, '%H:%i %d/%m/%Y') as TimeStr
            FROM Reservations r
            JOIN Customers c ON r.CustomerID = c.CustomerID
            WHERE r.TableID = %s 
              AND r.DateTime >= DATE_SUB(%s, INTERVAL 2 HOUR)
              AND r.DateTime <= DATE_ADD(%s, INTERVAL 2 HOUR)
        """, (data['table_id'], dt_str, dt_str))
        
        conflict = cursor.fetchone()
        if conflict:
            return {"status": "error", "message": f"Bàn này đã được khách '{conflict['CustomerName']}' giữ chỗ vào lúc {conflict['TimeStr']}. Các ca phục vụ phải cách nhau tối thiểu 2 tiếng!"}

        cursor.execute("""
            INSERT INTO Reservations (CustomerID, TableID, DateTime, GuestCount, Notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (data['customer_id'], data['table_id'], data['datetime'], data['guests'], data.get('notes', '')))
        
        cursor.execute("UPDATE Tables SET Status = 'Reserved' WHERE TableID = %s", (data['table_id'],))
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()

# 2. CẬP NHẬT LỊCH ĐẶT BÀN
@router.put("/api/reservations/{res_id}", include_in_schema=False)
async def api_update_reservation(res_id: int, request: Request, db: MySQLConnection = Depends(get_db)):
    data = await request.json()
    cursor = db.cursor(dictionary=True)
    try:
        dt_str = data['datetime'].replace('T', ' ')
        
        cursor.execute("""
            SELECT c.CustomerName, DATE_FORMAT(r.DateTime, '%H:%i %d/%m/%Y') as TimeStr
            FROM Reservations r
            JOIN Customers c ON r.CustomerID = c.CustomerID
            WHERE r.TableID = %s 
              AND r.DateTime >= DATE_SUB(%s, INTERVAL 2 HOUR)
              AND r.DateTime <= DATE_ADD(%s, INTERVAL 2 HOUR)
              AND r.ReservationID != %s
        """, (data['table_id'], dt_str, dt_str, res_id))
        
        conflict = cursor.fetchone()
        if conflict:
            return {"status": "error", "message": f"Bàn này đã được khách '{conflict['CustomerName']}' giữ chỗ vào lúc {conflict['TimeStr']}. Các ca phục vụ phải cách nhau 2 tiếng!"}

        cursor.execute("SELECT TableID FROM Reservations WHERE ReservationID = %s", (res_id,))
        old_res = cursor.fetchone()

        cursor.execute("""
            UPDATE Reservations 
            SET CustomerID=%s, TableID=%s, DateTime=%s, GuestCount=%s, Notes=%s 
            WHERE ReservationID=%s
        """, (data['customer_id'], data['table_id'], data['datetime'], data['guests'], data.get('notes', ''), res_id))

        if old_res and str(old_res['TableID']) != str(data['table_id']):
            cursor.execute("UPDATE Tables SET Status = 'Available' WHERE TableID = %s", (old_res['TableID'],))
            cursor.execute("UPDATE Tables SET Status = 'Reserved' WHERE TableID = %s", (data['table_id'],))

        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()

@router.delete("/api/reservations/{res_id}", include_in_schema=False)
def api_delete_reservation(res_id: int, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT TableID FROM Reservations WHERE ReservationID = %s", (res_id,))
        res_data = cursor.fetchone()
        if res_data:
            cursor.execute("DELETE FROM Reservations WHERE ReservationID = %s", (res_id,))
            cursor.execute("UPDATE Tables SET Status = 'Available' WHERE TableID = %s", (res_data["TableID"],))
            db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()

# ---------------------------------------------------------
# 5. CÁC API QUẢN LÝ HÓA ĐƠN (INVOICES & INVOICE DETAILS)
# ---------------------------------------------------------
@router.post("/api/invoices", include_in_schema=False)
async def api_create_invoice(request: Request, db: MySQLConnection = Depends(get_db)):
    data = await request.json()
    cursor = db.cursor()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        staff_id = data.get('staff_id')
        items = data.get('items', []) # Lấy danh sách món ăn từ giao diện
        
        if not staff_id:
            return {"status": "error", "message": "Không tìm thấy phiên đăng nhập. Vui lòng F5 hoặc đăng nhập lại."}

        if not items or len(items) == 0:
            return {"status": "error", "message": "Hóa đơn phải có ít nhất 1 món ăn!"}

        # 1. Tạo hóa đơn gốc
        cursor.execute("""
            INSERT INTO Invoices (CustomerID, TableID, TotalAmount, PaymentMethod, PaymentDate, StaffID)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data['customer_id'], data['table_id'], data['total'], data['payment'], now, staff_id))
        
        # 2. Lấy ID của hóa đơn vừa tạo để lưu chi tiết món
        invoice_id = cursor.lastrowid
        
        for item in items:
            cursor.execute("""
                INSERT INTO InvoiceDetails (InvoiceID, DishID, Quantity, UnitPrice)
                VALUES (%s, %s, %s, %s)
            """, (invoice_id, item['dish_id'], item['quantity'], item['price']))
            
        # 3. Khách thanh toán xong -> Tự động chuyển Bàn về trạng thái Trống (Available)
        cursor.execute("UPDATE Tables SET Status = 'Available' WHERE TableID = %s", (data['table_id'],))

        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()

# API: LẤY CHI TIẾT MÓN ĂN ĐỂ IN BILL & ĐỔ VÀO FORM SỬA
@router.get("/api/invoices/{inv_id}/details", include_in_schema=False)
def api_get_invoice_details(inv_id: int, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        # Bổ sung id.DishID để Frontend nhận diện được món ăn khi Sửa
        cursor.execute("""
            SELECT id.DishID, md.DishName, id.Quantity, id.UnitPrice, (id.Quantity * id.UnitPrice) as SubTotal
            FROM InvoiceDetails id
            JOIN MenuItems md ON id.DishID = md.DishID
            WHERE id.InvoiceID = %s
        """, (inv_id,))
        items = cursor.fetchall()
        return {"status": "success", "items": items}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()

# API: CẬP NHẬT HÓA ĐƠN (WIPE & REWRITE CHI TIẾT MÓN)
@router.put("/api/invoices/{inv_id}", include_in_schema=False)
async def api_update_invoice(inv_id: int, request: Request, db: MySQLConnection = Depends(get_db)):
    data = await request.json()
    cursor = db.cursor()
    try:
        # 1. Cập nhật thông tin chung của Hóa đơn
        cursor.execute("""
            UPDATE Invoices 
            SET CustomerID=%s, TableID=%s, TotalAmount=%s, PaymentMethod=%s
            WHERE InvoiceID=%s
        """, (data['customer_id'], data['table_id'], data['total'], data['payment'], inv_id))
        
        # 2. Xóa sạch chi tiết món cũ của hóa đơn này
        cursor.execute("DELETE FROM InvoiceDetails WHERE InvoiceID = %s", (inv_id,))
        
        # 3. Ghi lại danh sách món mới từ giỏ hàng
        items = data.get('items', [])
        for item in items:
            cursor.execute("""
                INSERT INTO InvoiceDetails (InvoiceID, DishID, Quantity, UnitPrice)
                VALUES (%s, %s, %s, %s)
            """, (inv_id, item['dish_id'], item['quantity'], item['price']))

        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()

@router.delete("/api/invoices/{inv_id}", include_in_schema=False)
def api_delete_invoice(inv_id: int, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM InvoiceDetails WHERE InvoiceID = %s", (inv_id,))
        cursor.execute("DELETE FROM Invoices WHERE InvoiceID = %s", (inv_id,))
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()