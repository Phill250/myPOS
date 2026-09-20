from datetime import datetime, date
from pydantic import BaseModel, ConfigDict

class LibraryRentalBase(BaseModel):
    expected_return: date
    actual_return: date | None = None
    customer_id: int
    user_id: int

class LibraryRentalCreate(LibraryRentalBase):
    pass

class LibraryRentalUpdate(BaseModel):
    """Only the return dates can be changed after a rental is created —
    e.g. extending the due date or recording the actual return.
    customer_id and user_id are fixed at checkout time."""
    expected_return: date | None = None
    actual_return: date | None = None

class LibraryRentalRead(LibraryRentalBase):
    model_config = ConfigDict(from_attributes=True)
    
    rental_id: int
    rental_timestamp: datetime