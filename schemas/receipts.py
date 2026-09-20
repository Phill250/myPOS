from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ReceiptBase(BaseModel):
    receipt_number: str
    sale_id: int | None = None
    rental_id: int | None = None

class ReceiptCreate(ReceiptBase):
    pass

class ReceiptUpdate(BaseModel):
    """sale_id and rental_id are fixed at creation time — a receipt should
    always point to the transaction it was actually printed for."""
    receipt_number: str | None = None

class ReceiptRead(ReceiptBase):
    model_config = ConfigDict(from_attributes=True)
    
    receipt_id: int
    printed_at: datetime