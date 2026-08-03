from pydantic import BaseModel, ConfigDict

class RetailSaleItemBase(BaseModel):
    sale_id: int
    book_id: int
    quantity: int
    price_snapshot: float

class RetailSaleItemCreate(RetailSaleItemBase):
    pass

class RetailSaleItemUpdate(BaseModel):
    sale_id: int | None = None
    book_id: int | None = None
    quantity: int | None = None
    price_snapshot: float | None = None

class RetailSaleItemRead(RetailSaleItemBase):
    model_config = ConfigDict(from_attributes=True)
    
    sale_item_id: int
