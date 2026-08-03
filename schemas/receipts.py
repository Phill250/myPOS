from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ReceiptBase(BaseModel):
    receipt_number: str
    sale_id: int | None = None
    rental_id: int | None = None

class ReceiptCreate(ReceiptBase):
    pass

class ReceiptUpdate(BaseModel):
    receipt_number: str | None = None
    sale_id: int | None = None
    rental_id: int | None = None

class ReceiptRead(ReceiptBase):
    model_config = ConfigDict(from_attributes=True)
    
    receipt_id: int
    printed_at: datetime
