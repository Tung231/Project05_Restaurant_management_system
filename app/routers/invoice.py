from fastapi import APIRouter, Depends, HTTPException
from mysql.connector.connection import MySQLConnection
from mysql.connector import Error as MySQLError

from app.core.database import get_db
from app.schemas import invoice as schemas
from app.crud import invoice as crud

router = APIRouter(prefix="/invoices", tags=["Quản lý Hóa đơn & Thanh toán"])

@router.get("/{invoice_id}", response_model=schemas.InvoiceResponse)
def get_single_invoice(invoice_id: int, db: MySQLConnection = Depends(get_db)):
    """Lấy thông tin một hóa đơn bao gồm cả chi tiết các món ăn"""
    db_invoice = crud.get_invoice(db, invoice_id)
    if db_invoice is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy hóa đơn số {invoice_id}")
    return db_invoice

@router.post("/", response_model=schemas.InvoiceResponse, status_code=201)
def create_new_invoice(invoice: schemas.InvoiceCreate, db: MySQLConnection = Depends(get_db)):
    """
    Tạo hóa đơn mới. 
    Lưu ý: Payload gửi lên phải chứa mảng 'details' gồm các món ăn. TotalAmount sẽ do CSDL tự tính.
    """
    try:
        return crud.create_invoice(db, invoice)
    except ValueError as ve:
        # Bắt lỗi bảo mật: Món ăn không tồn tại từ hàm CRUD
        raise HTTPException(status_code=400, detail=str(ve))
    except MySQLError as me:
        # Bắt lỗi CSDL trong quá trình chạy Transaction
        raise HTTPException(status_code=400, detail=f"Lỗi thao tác dữ liệu: {str(me)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống nội bộ: {str(e)}")
    
@router.get("/")
def get_all_invoices(db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Invoices ORDER BY InvoiceID DESC")
    invoices = cursor.fetchall()
    cursor.close()
    return invoices

@router.put("/{invoice_id}")
def update_invoice_status(invoice_id: int, payment_status: str, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("UPDATE Invoices SET PaymentStatus = %s WHERE InvoiceID = %s", (payment_status, invoice_id))
    db.commit()
    cursor.close()
    return {"message": "Cập nhật trạng thái thanh toán thành công"}

@router.delete("/{invoice_id}")
def delete_invoice(invoice_id: int, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    # Phải xóa chi tiết hóa đơn (khóa ngoại) trước, rồi mới xóa hóa đơn
    cursor.execute("DELETE FROM InvoiceItems WHERE InvoiceID = %s", (invoice_id,))
    cursor.execute("DELETE FROM Invoices WHERE InvoiceID = %s", (invoice_id,))
    db.commit()
    cursor.close()
    return {"message": f"Đã hủy và xóa hóa đơn số {invoice_id}"}