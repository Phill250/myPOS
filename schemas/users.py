from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    role: str
    is_active: bool = True


class UserCreate(BaseModel):
    """Used for public self-registration (/users/register).
    No role/is_active here — those are always set server-side."""
    username: str
    password: str


class UserCreateByAdmin(UserBase):
    """Used only by the super-admin-only create endpoint (/users/, POST).
    Lets the admin set role and is_active explicitly."""
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    role: str | None = None
    is_active: bool | None = None
    password: str | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: int