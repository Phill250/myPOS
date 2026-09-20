from datetime import datetime
from pydantic import BaseModel, ConfigDict

class RetailSaleBase(BaseModel):
    total_amount: int
    customer_id: int | None = None
    user_id: int

class RetailSaleCreate(RetailSaleBase):
    pass

class RetailSaleUpdate(BaseModel):
    """Only total_amount can be corrected after a sale is created.
    customer_id and user_id are fixed at creation time and cannot be
    reassigned — the sale record should reflect who was actually involved."""
    total_amount: int | None = None

class RetailSaleRead(RetailSaleBase):
    model_config = ConfigDict(from_attributes=True)
    
    sale_id: int
    sale_timestamp: datetime