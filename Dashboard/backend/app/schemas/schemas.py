from pydantic import BaseModel
from typing import Optional

class ClassBase(BaseModel):
    name: str
    description: Optional[str] = None

class ClassCreate(ClassBase):
    pass

class ClassResponse(ClassBase):
    id: int
    
    class Config:
        from_attributes = True

class PaymentApproveReject(BaseModel):
    reason: Optional[str] = None