from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

# 1. Base Schema (Chứa các trường dùng chung)
class CustomerBase(BaseModel):
    # Ràng buộc độ dài để khớp với VARCHAR(255) và VARCHAR(20) trong MySQL
    CustomerName: str = Field(..., max_length=255, description="Tên đầy đủ của khách hàng")
    PhoneNumber: str = Field(..., max_length=20, description="Số điện thoại liên hệ")
    Address: Optional[str] = Field(None, max_length=255, description="Địa chỉ khách hàng (có thể trống)")

# 2. Schema dùng khi nhận request tạo mới khách hàng
class CustomerCreate(CustomerBase):
    pass # Kế thừa nguyên bản từ CustomerBase

# 3. Schema dùng khi nhận request cập nhật (Sửa thông tin)
# Tất cả các trường đều là Optional, vì khách có thể chỉ muốn đổi mỗi số điện thoại
class CustomerUpdate(BaseModel):
    CustomerName: Optional[str] = Field(None, max_length=255)
    PhoneNumber: Optional[str] = Field(None, max_length=20)
    Address: Optional[str] = Field(None, max_length=255)

# 4. Schema dùng để trả dữ liệu về cho người dùng (Response)
class CustomerResponse(CustomerBase):
    CustomerID: int
    
    # Cấu hình from_attributes=True (Pydantic v2) giúp tự động chuyển 
    # dữ liệu lấy từ Database (dạng Tuple/Dict) thành Object JSON để trả về.
    model_config = ConfigDict(from_attributes=True)