from mysql.connector.connection import MySQLConnection
from typing import List, Optional
from app.schemas import invoice as schemas

def get_invoice(db: MySQLConnection, invoice_id: int) -> Optional[dict]:
    cursor = db.cursor(dictionary=True)
    
    # 1. Lấy thông tin hóa đơn tổng (Bảng Invoices)
    cursor.execute("SELECT * FROM Invoices WHERE InvoiceID = %s", (invoice_id,))
    invoice = cursor.fetchone()
    
    if not invoice:
        cursor.close()
        return None
        
    # 2. Lấy danh sách chi tiết các món ăn (Bảng InvoiceDetails)
    cursor.execute("SELECT * FROM InvoiceDetails WHERE InvoiceID = %s", (invoice_id,))
    details = cursor.fetchall()
    cursor.close()
    
    # 3. Ép vào thành 1 cục (Nested Dictionary) để Schema Pydantic tự động đọc được
    invoice["details"] = details
    return invoice

def create_invoice(db: MySQLConnection, invoice: schemas.InvoiceCreate) -> dict:
    cursor = db.cursor(dictionary=True)
    
    try:
        # BẬT GIAO DỊCH (TRANSACTION)
        db.start_transaction()
        
        # BƯỚC 1: Tạo hóa đơn mẹ
        query_invoice = """
            INSERT INTO Invoices (CustomerID, TableID, StaffID, ReservationID, PaymentMethod) 
            VALUES (%s, %s, %s, %s, %s)
        """
        values_invoice = (
            invoice.CustomerID, invoice.TableID, invoice.StaffID, 
            invoice.ReservationID, invoice.PaymentMethod
        )
        cursor.execute(query_invoice, values_invoice)
        new_invoice_id = cursor.lastrowid
        
        # BƯỚC 2: Kiểm tra giá thật & Chuẩn bị dữ liệu chèn hàng loạt
        values_details = []
        for detail in invoice.details:
            # Query giá gốc từ hệ thống để chống gian lận
            cursor.execute("SELECT Price FROM MenuItems WHERE DishID = %s", (detail.DishID,))
            dish = cursor.fetchone()
            
            # Kích hoạt báo lỗi nếu Frontend gửi mã món ăn linh tinh
            if not dish:
                raise ValueError(f"Lỗi: Món ăn với mã DishID {detail.DishID} không tồn tại!")
                
            # Dùng dish["Price"] (giá của DB) thay vì detail.UnitPrice (giá của Frontend)
            values_details.append(
                (new_invoice_id, detail.DishID, detail.Quantity, dish["Price"])
            )
            
        query_details = """
            INSERT INTO InvoiceDetails (InvoiceID, DishID, Quantity, UnitPrice) 
            VALUES (%s, %s, %s, %s)
        """
        # Thực thi nhồi toàn bộ món ăn vào DB
        cursor.executemany(query_details, values_details)
        
        # BƯỚC 3: Gọi thủ tục tính tổng tiền
        cursor.callproc('sp_GenerateBill', (new_invoice_id, 0.0, 0.0))
        
        # CHỐT LƯU
        db.commit()
        
    except Exception as e:
        # CÓ LỖI -> HỦY BỎ TOÀN BỘ
        db.rollback()
        raise e
    finally:
        cursor.close()
        
    return get_invoice(db, new_invoice_id)