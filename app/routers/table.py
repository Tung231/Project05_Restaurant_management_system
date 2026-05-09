from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from mysql.connector.connection import MySQLConnection
from app.core.database import get_db

router = APIRouter(prefix="/tables", tags=["Table Management"])

class TableBase(BaseModel):
    TableNumber: str
    Capacity: int
    Status: str = "Available"

class TableUpdate(BaseModel):
    TableNumber: Optional[str] = None
    Capacity: Optional[int] = None
    Status: Optional[str] = None

@router.post("/")
def create_table(table: TableBase, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO Tables (TableNumber, Capacity, Status) VALUES (%s, %s, %s)", 
        (table.TableNumber, table.Capacity, table.Status)
    )
    db.commit()
    cursor.close()
    return {"message": "Thêm bàn thành công"}

@router.put("/{table_id}")
def update_table(table_id: int, table: TableUpdate, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    if table.TableNumber:
        cursor.execute("UPDATE Tables SET TableNumber = %s WHERE TableID = %s", (table.TableNumber, table_id))
    if table.Capacity is not None:
        cursor.execute("UPDATE Tables SET Capacity = %s WHERE TableID = %s", (table.Capacity, table_id))
    if table.Status:
        cursor.execute("UPDATE Tables SET Status = %s WHERE TableID = %s", (table.Status, table_id))
    db.commit()
    cursor.close()
    return {"message": "Cập nhật bàn thành công"}