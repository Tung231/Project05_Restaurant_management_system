from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal

# ==========================================
# CATEGORY SCHEMAS (PHÂN LOẠI MÓN ĂN)
# ==========================================
class CategoryBase(BaseModel):
    CategoryName: str = Field(..., max_length=100)
    Description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    CategoryName: Optional[str] = Field(None, max_length=100)
    Description: Optional[str] = None

class CategoryResponse(CategoryBase):
    CategoryID: int
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# MENU ITEM SCHEMAS (CHI TIẾT MÓN ĂN)
# ==========================================
class MenuItemBase(BaseModel):
    DishName: str = Field(..., max_length=255)
    # Ràng buộc số tiền phải lớn hơn 0 và dùng Decimal cho chính xác
    Price: Decimal = Field(..., gt=0, description="Giá bán của món ăn")
    CategoryID: int = Field(..., description="ID của danh mục phân loại")

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    DishName: Optional[str] = Field(None, max_length=255)
    Price: Optional[Decimal] = Field(None, gt=0)
    CategoryID: Optional[int] = None

class MenuItemResponse(MenuItemBase):
    DishID: int
    
    model_config = ConfigDict(from_attributes=True)