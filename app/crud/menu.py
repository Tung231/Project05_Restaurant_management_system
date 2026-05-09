from mysql.connector.connection import MySQLConnection
from typing import List, Optional
from app.schemas import menu as schemas

# ==========================================
# THAO TÁC VỚI CATEGORIES
# ==========================================
def get_categories(db: MySQLConnection) -> List[dict]:
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Categories")
    results = cursor.fetchall()
    cursor.close()
    return results

# Thêm hàm này để tái sử dụng
def get_category(db: MySQLConnection, category_id: int) -> Optional[dict]:
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Categories WHERE CategoryID = %s", (category_id,))
    result = cursor.fetchone()
    cursor.close()
    return result

def create_category(db: MySQLConnection, category: schemas.CategoryCreate) -> dict:
    cursor = db.cursor(dictionary=True)
    query = "INSERT INTO Categories (CategoryName, Description) VALUES (%s, %s)"
    cursor.execute(query, (category.CategoryName, category.Description))
    db.commit()
    
    new_id = cursor.lastrowid
    cursor.close()
    
    # Tái sử dụng hàm get_category cực kỳ gọn gàng và chuẩn pattern
    return get_category(db, new_id)

# ==========================================
# THAO TÁC VỚI MENU ITEMS
# ==========================================
def get_menu_items(db: MySQLConnection, skip: int = 0, limit: int = 100) -> List[dict]:
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM MenuItems LIMIT %s OFFSET %s"
    cursor.execute(query, (limit, skip))
    results = cursor.fetchall()
    cursor.close()
    return results

def get_menu_item(db: MySQLConnection, dish_id: int) -> Optional[dict]:
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM MenuItems WHERE DishID = %s"
    cursor.execute(query, (dish_id,))
    result = cursor.fetchone()
    cursor.close()
    return result

def create_menu_item(db: MySQLConnection, item: schemas.MenuItemCreate) -> dict:
    cursor = db.cursor(dictionary=True)
    query = """
        INSERT INTO MenuItems (DishName, Price, CategoryID) 
        VALUES (%s, %s, %s)
    """
    # item.Price đang là Decimal nhờ Pydantic, chèn thẳng vào MySQL 
    values = (item.DishName, item.Price, item.CategoryID)
    cursor.execute(query, values)
    db.commit()
    
    new_id = cursor.lastrowid
    cursor.close()
    
    return get_menu_item(db, new_id)