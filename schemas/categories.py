from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

class CategoryBase(BaseModel):

    category_name: str
    description: str | None = None
   
    

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    category_name: str | None = None
    description: str | None = None
        
class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    
    category_id:int

    