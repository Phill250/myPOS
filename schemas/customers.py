from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: str | None = None
    library_member: bool
    user_id: int | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    email: str | None = None
    library_member: bool | None = None
    user_id: int | None = None


class CustomerRead(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    customer_id: int