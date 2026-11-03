from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    isbn: str | None = None
    sale_price: Decimal = Field(ge=0)
    category_id: int
    supplier_id: int
    retail_stock: int = Field(default=0, ge=0)
    library_stock: int = Field(default=0, ge=0)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    author: str | None = Field(default=None, min_length=1)
    isbn: str | None = None
    sale_price: Decimal | None = Field(default=None, ge=0)
    category_id: int | None = None
    supplier_id: int | None = None
    retail_stock: int | None = Field(default=None, ge=0)
    library_stock: int | None = Field(default=None, ge=0)


class BookRead(BookBase):
    model_config = ConfigDict(from_attributes=True)

    book_id: int
