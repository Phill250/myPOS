from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from schemas.customers import CustomerRead

Role = Literal["customer", "staff", "super_admin"]


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    role: Role
    is_active: bool = True


class UserCreate(BaseModel):
    """Used for public self-registration (/users/register).
    No role/is_active here — those are always set server-side."""

    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1)


class UserCreateByAdmin(UserBase):
    """Used only by the super-admin-only create endpoint (/users/, POST).
    Lets the admin set role and is_active explicitly."""

    password: str = Field(min_length=1)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    role: Role | None = None
    is_active: bool | None = None
    password: str | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: int


class MeRead(UserRead):
    """The logged-in user, plus their linked customer profile (if any)."""

    customer_profile: CustomerRead | None = None
