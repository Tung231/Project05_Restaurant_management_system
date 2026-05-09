from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from mysql.connector.connection import MySQLConnection
from app.core.database import get_db

router = APIRouter(prefix="/reservations", tags=["Reservations"])

class ReservationCreate(BaseModel):
    CustomerID: int
    TableID: int
    DateTime: str
    GuestCount: int

@router.post("/")
def create_reservation(res: ReservationCreate, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO Reservations (CustomerID, TableID, DateTime, GuestCount) VALUES (%s, %s, %s, %s)", 
        (res.CustomerID, res.TableID, res.DateTime, res.GuestCount)
    )
    db.commit()
    cursor.close()
    return {"message": "Đặt bàn thành công"}