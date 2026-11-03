from pydantic import BaseModel, ConfigDict, Field


class RetailSaleItemBase(BaseModel):
    sale_id: int
    book_id: int
    quantity: int = Field(gt=0)
    price_snapshot: float = Field(ge=0)


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
