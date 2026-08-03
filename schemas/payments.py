from pydantic import BaseModel, ConfigDict

class PaymentBase(BaseModel):
    amount: float
    payment_method: str
    transaction_type: str
    sale_id: int | None = None
    rental_id: int | None = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    amount: float | None = None
    payment_method: str | None = None
    transaction_type: str | None = None
    sale_id: int | None = None
    rental_id: int | None = None

class PaymentRead(PaymentBase):
    model_config = ConfigDict(from_attributes=True)
    
    payment_id: int
