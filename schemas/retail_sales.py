from datetime import datetime
from pydantic import BaseModel, ConfigDict

class RetailSaleBase(BaseModel):
    total_amount: int
    customer_id: int | None = None
    user_id: int

class RetailSaleCreate(RetailSaleBase):
    pass

class RetailSaleUpdate(BaseModel):
    total_amount: int | None = None
    customer_id: int | None = None
    user_id: int | None = None

class RetailSaleRead(RetailSaleBase):
    model_config = ConfigDict(from_attributes=True)
    
    sale_id: int
    sale_timestamp: datetime
