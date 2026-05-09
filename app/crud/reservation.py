from mysql.connector.connection import MySQLConnection
from typing import List, Optional
from app.schemas import reservation as schemas

def get_reservations(db: MySQLConnection, skip: int = 0, limit: int = 100) -> List[dict]:
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Reservations ORDER BY DateTime DESC LIMIT %s OFFSET %s", (limit, skip))
    results = cursor.fetchall()
    cursor.close()
    return results

def get_reservation(db: MySQLConnection, reservation_id: int) -> Optional[dict]:
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Reservations WHERE ReservationID = %s", (reservation_id,))
    result = cursor.fetchone()
    cursor.close()
    return result

def create_reservation(db: MySQLConnection, reservation: schemas.ReservationCreate) -> dict:
    cursor = db.cursor(dictionary=True)
    query = """
        INSERT INTO Reservations (CustomerID, TableID, DateTime, GuestCount) 
        VALUES (%s, %s, %s, %s)
    """
    values = (
        reservation.CustomerID, 
        reservation.TableID, 
        reservation.DateTime, 
        reservation.GuestCount
    )
    cursor.execute(query, values)
    db.commit()
    
    new_id = cursor.lastrowid
    cursor.close()
    
    return get_reservation(db, new_id)