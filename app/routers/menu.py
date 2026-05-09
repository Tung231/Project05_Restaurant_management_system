from fastapi import APIRouter, Depends, HTTPException
from typing import List
from mysql.connector.connection import MySQLConnection
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.schemas import menu as schemas
from app.crud import menu as crud

router = APIRouter(prefix="/menu", tags=["Quản lý Thực đơn"])

# ==========================================
# CÁC ENDPOINT CHO DANH MỤC (CATEGORIES)
# ==========================================
@router.get("/categories", response_model=List[schemas.CategoryResponse])
def get_list_categories(db: MySQLConnection = Depends(get_db)):
    """Lấy danh sách các phân loại món ăn"""
    return crud.get_categories(db)

@router.post("/categories", response_model=schemas.CategoryResponse, status_code=201)
def create_new_category(category: schemas.CategoryCreate, db: MySQLConnection = Depends(get_db)):
    """Tạo mới một danh mục món ăn"""
    return crud.create_category(db, category)


# ==========================================
# CÁC ENDPOINT CHO MÓN ĂN (MENU ITEMS)
# ==========================================
@router.get("/items", response_model=List[schemas.MenuItemResponse])
def get_list_menu_items(skip: int = 0, limit: int = 100, db: MySQLConnection = Depends(get_db)):
    """Lấy danh sách tất cả món ăn trong thực đơn"""
    return crud.get_menu_items(db, skip=skip, limit=limit)

@router.get("/items/{dish_id}", response_model=schemas.MenuItemResponse)
def get_single_menu_item(dish_id: int, db: MySQLConnection = Depends(get_db)):
    """Lấy chi tiết một món ăn"""
    db_item = crud.get_menu_item(db, dish_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Món ăn không tồn tại")
    return db_item

@router.post("/items", response_model=schemas.MenuItemResponse, status_code=201)
def create_new_menu_item(item: schemas.MenuItemCreate, db: MySQLConnection = Depends(get_db)):
    """Thêm một món ăn mới vào thực đơn"""
    try:
        return crud.create_menu_item(db, item)
    except Exception as e:
        # Bắt lỗi Foreign Key nếu CategoryID truyền lên không tồn tại
        raise HTTPException(status_code=400, detail=f"Không thể tạo món ăn. Lỗi từ hệ thống: {str(e)}")
    
class MenuItemUpdate(BaseModel):
    DishName: Optional[str] = None
    Price: Optional[float] = None
    CategoryID: Optional[int] = None

@router.put("/items/{item_id}")
def update_menu_item(item_id: int, item: MenuItemUpdate, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    if item.DishName:
        cursor.execute("UPDATE MenuItems SET DishName = %s WHERE DishID = %s", (item.DishName, item_id))
    if item.Price:
        cursor.execute("UPDATE MenuItems SET Price = %s WHERE DishID = %s", (item.Price, item_id))
    if item.CategoryID:
        cursor.execute("UPDATE MenuItems SET CategoryID = %s WHERE DishID = %s", (item.CategoryID, item_id))
    db.commit()
    cursor.close()
    return {"message": "Cập nhật món ăn thành công"}

@router.delete("/items/{item_id}")
def delete_menu_item(item_id: int, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM MenuItems WHERE DishID = %s", (item_id,))
        db.commit()
        return {"message": "Đã xóa món ăn khỏi thực đơn"}
    except Exception as e:
        return {"error": "Không thể xóa món ăn này vì nó đang nằm trong hóa đơn của khách!"}
    finally:
        cursor.close()

class CategoryUpdate(BaseModel):
    CategoryName: str

@router.put("/categories/{category_id}")
def update_category(category_id: int, category: CategoryUpdate, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("UPDATE MenuCategories SET CategoryName = %s WHERE CategoryID = %s", (category.CategoryName, category_id))
    db.commit()
    cursor.close()
    return {"message": "Cập nhật danh mục thành công"}

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM MenuCategories WHERE CategoryID = %s", (category_id,))
        db.commit()
        return {"message": "Đã xóa danh mục"}
    except Exception as e:
        return {"error": "Không thể xóa danh mục này vì đang có món ăn bên trong! Vui lòng xóa món ăn trước."}
    finally:
        cursor.close()