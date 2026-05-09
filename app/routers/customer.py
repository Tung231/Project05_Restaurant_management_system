from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from mysql.connector.connection import MySQLConnection
from app.core.database import get_db

router = APIRouter(prefix="/customers", tags=["Customer Management"])

# Cập nhật Schema cho khớp với Javascript và Database
class CustomerBase(BaseModel):
    CustomerName: str
    PhoneNumber: str
    Address: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    CustomerName: Optional[str] = None
    PhoneNumber: Optional[str] = None
    Address: Optional[str] = None

@router.post("/")
def create_customer(customer: CustomerCreate, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO Customers (CustomerName, PhoneNumber, Address) VALUES (%s, %s, %s)", 
        (customer.CustomerName, customer.PhoneNumber, customer.Address)
    )
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    return {"message": "Thêm khách hàng thành công", "CustomerID": new_id}

@router.put("/{customer_id}")
def update_customer(customer_id: int, customer: CustomerUpdate, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    if customer.CustomerName:
        cursor.execute("UPDATE Customers SET CustomerName = %s WHERE CustomerID = %s", (customer.CustomerName, customer_id))
    if customer.PhoneNumber:
        cursor.execute("UPDATE Customers SET PhoneNumber = %s WHERE CustomerID = %s", (customer.PhoneNumber, customer_id))
    if customer.Address is not None:
        cursor.execute("UPDATE Customers SET Address = %s WHERE CustomerID = %s", (customer.Address, customer_id))
    db.commit()
    cursor.close()
    return {"message": f"Cập nhật khách hàng {customer_id} thành công"}

@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Customers WHERE CustomerID = %s", (customer_id,))
        db.commit()
        return {"message": "Xóa thành công"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Không thể xóa khách hàng đã có hóa đơn/đặt bàn.")
    finally:
        cursor.close()