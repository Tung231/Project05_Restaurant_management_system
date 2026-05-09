from mysql.connector.connection import MySQLConnection
from app.schemas import table as schemas

def get_tables(db: MySQLConnection):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Tables")
    result = cursor.fetchall()
    cursor.close()
    return result

def get_table(db: MySQLConnection, table_id: int):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Tables WHERE TableID = %s", (table_id,))
    result = cursor.fetchone()
    cursor.close()
    return result

def create_table(db: MySQLConnection, table: schemas.TableCreate):
    cursor = db.cursor()
    cursor.execute("INSERT INTO Tables (TableNumber, Capacity, Status) VALUES (%s, %s, %s)", 
                   (table.TableNumber, table.Capacity, table.Status))
    db.commit()
    table_id = cursor.lastrowid
    cursor.close()
    return table_id

def update_table(db: MySQLConnection, table_id: int, table: schemas.TableUpdate):
    cursor = db.cursor()
    updates = []
    params = []
    if table.TableNumber is not None:
        updates.append("TableNumber = %s")
        params.append(table.TableNumber)
    if table.Capacity is not None:
        updates.append("Capacity = %s")
        params.append(table.Capacity)
    if table.Status is not None:
        updates.append("Status = %s")
        params.append(table.Status)
    if updates:
        query = f"UPDATE Tables SET {', '.join(updates)} WHERE TableID = %s"
        params.append(table_id)
        cursor.execute(query, params)
        db.commit()
    cursor.close()

def delete_table(db: MySQLConnection, table_id: int):
    cursor = db.cursor()
    cursor.execute("DELETE FROM Tables WHERE TableID = %s", (table_id,))
    db.commit()
    cursor.close()