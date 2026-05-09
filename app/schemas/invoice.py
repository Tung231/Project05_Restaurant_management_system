from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

# ==========================================
# 1. INVOICE DETAIL SCHEMAS (CHI TIẾT MÓN ĂN)
# ==========================================
class InvoiceDetailBase(BaseModel):
    DishID: int
    Quantity: int = Field(..., gt=0, description="Số lượng món phải lớn hơn 0")
    UnitPrice: Decimal = Field(..., gt=0, description="Đơn giá tại thời điểm xuất hóa đơn")

class InvoiceDetailCreate(BaseModel): # Đổi thành kế thừa từ BaseModel thay vì Base
    DishID: int
    Quantity: int = Field(..., gt=0, description="Số lượng món phải lớn hơn 0")
    # ĐÃ XÓA UnitPrice ở đây vì backend tự lo

class InvoiceDetailResponse(InvoiceDetailBase):
    InvoiceDetailID: int
    InvoiceID: int
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 2. INVOICE SCHEMAS (HÓA ĐƠN TỔNG)
# ==========================================
class InvoiceBase(BaseModel):
    CustomerID: int
    TableID: int
    StaffID: int
    # ReservationID cho phép null đối với khách vãng lai
    ReservationID: Optional[int] = None
    PaymentMethod: Optional[str] = Field(None, max_length=50)

class InvoiceCreate(InvoiceBase):
    # ĐÂY LÀ ĐIỂM KỸ THUẬT QUAN TRỌNG: 
    # Khai báo một mảng (List) chứa các món ăn. 
    # Khi user gửi JSON để tạo hóa đơn, nó sẽ hứng cả 1 cục dữ liệu lồng nhau.
    details: List[InvoiceDetailCreate] = Field(
        ..., 
        min_length=1, 
        description="Hóa đơn phải có ít nhất 1 món ăn"
    )

class InvoiceUpdate(BaseModel):
    # Thường chỉ cho phép cập nhật ngày thanh toán và phương thức
    PaymentDate: Optional[datetime] = None
    PaymentMethod: Optional[str] = Field(None, max_length=50)

class InvoiceResponse(InvoiceBase):
    InvoiceID: int
    TotalAmount: Decimal
    PaymentDate: Optional[datetime] = None
    
    # Trả về luôn danh sách các món ăn trực thuộc hóa đơn này cho Frontend hiển thị
    details: List[InvoiceDetailResponse] = []
    
    model_config = ConfigDict(from_attributes=True)