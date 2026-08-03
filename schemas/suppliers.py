from pydantic import BaseModel, ConfigDict

class SupplierBase(BaseModel):
    company_name: str
    phone_number: str

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    company_name: str | None = None
    phone_number: str | None = None

class SupplierRead(SupplierBase):
    model_config = ConfigDict(from_attributes=True)
    
    supplier_id: int
