from mysql.connector.connection import MySQLConnection
from typing import List, Optional
from app.schemas import customer as schemas

def get_customer(db: MySQLConnection, customer_id: int) -> Optional[dict]:
    # Sử dụng dictionary=True để MySQL trả về { "CustomerID": 1, ... } thay vì Tuple (1, ...)
    # Điều này giúp Pydantic Schema convert dữ liệu dễ dàng.
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM Customers WHERE CustomerID = %s"
    cursor.execute(query, (customer_id,))
    result = cursor.fetchone()
    cursor.close()
    return result

def get_customers(db: MySQLConnection, skip: int = 0, limit: int = 100) -> List[dict]:
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM Customers LIMIT %s OFFSET %s"
    cursor.execute(query, (limit, skip))
    results = cursor.fetchall()
    cursor.close()
    return results

def create_customer(db: MySQLConnection, customer: schemas.CustomerCreate) -> dict:
    cursor = db.cursor(dictionary=True)
    query = """
        INSERT INTO Customers (CustomerName, PhoneNumber, Address) 
        VALUES (%s, %s, %s)
    """
    values = (customer.CustomerName, customer.PhoneNumber, customer.Address)
    cursor.execute(query, values)
    db.commit() # Phải commit để lưu xuống database
    
    new_id = cursor.lastrowid # Lấy ra ID vừa được tự động sinh (AUTO_INCREMENT)
    cursor.close()
    
    return get_customer(db, new_id)

def update_customer(db: MySQLConnection, customer_id: int, customer: schemas.CustomerUpdate) -> Optional[dict]:
    # Dùng exclude_unset=True để chỉ lấy những trường user thực sự gửi lên
    update_data = customer.model_dump(exclude_unset=True)
    
    if not update_data:
        return get_customer(db, customer_id)
        
    set_clauses = []
    values = []
    
    for key, value in update_data.items():
        set_clauses.append(f"{key} = %s")
        values.append(value)
        
    values.append(customer_id)
    
    query = f"UPDATE Customers SET {', '.join(set_clauses)} WHERE CustomerID = %s"
    
    cursor = db.cursor()
    cursor.execute(query, tuple(values))
    db.commit()
    cursor.close()
    
    return get_customer(db, customer_id)