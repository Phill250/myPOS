from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    username: str
    role: str
    is_active: bool = True

class UserCreate(UserBase):
    password_hash: str

class UserUpdate(BaseModel):
    username: str | None = None
    role: str | None = None
    is_active: bool | None = None
    password_hash: str | None = None

class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    user_id: int
