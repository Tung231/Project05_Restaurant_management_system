from pydantic import BaseModel
from typing import Optional

class TableBase(BaseModel):
    TableNumber: str
    Capacity: int
    Status: str = "Available"

class TableCreate(TableBase):
    pass

class TableUpdate(BaseModel):
    TableNumber: Optional[str] = None
    Capacity: Optional[int] = None
    Status: Optional[str] = None

class TableResponse(TableBase):
    TableID: int