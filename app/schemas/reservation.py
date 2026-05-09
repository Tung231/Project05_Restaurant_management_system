from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class ReservationBase(BaseModel):
    CustomerID: int = Field(..., description="ID của khách hàng")
    TableID: int = Field(..., description="ID của bàn được đặt")
    # Pydantic tự động validate chuỗi ngày giờ hợp lệ
    DateTime: datetime = Field(..., description="Ngày giờ đặt bàn (VD: 2026-05-15T19:00:00)")
    # Ép buộc số lượng khách phải từ 1 trở lên
    GuestCount: int = Field(..., gt=0, description="Số lượng khách tối thiểu là 1")

class ReservationCreate(ReservationBase):
    pass

class ReservationUpdate(BaseModel):
    CustomerID: Optional[int] = None
    TableID: Optional[int] = None
    DateTime: Optional[datetime] = None
    GuestCount: Optional[int] = Field(None, gt=0)

class ReservationResponse(ReservationBase):
    ReservationID: int
    
    model_config = ConfigDict(from_attributes=True)